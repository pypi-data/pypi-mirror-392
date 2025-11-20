# src/query_optimizer/adapters/postgres.py
import psycopg2
import json
import sqlparse
import re
from typing import Dict, Any, List, Optional, Tuple
from ..core.analyzer import DatabaseAdapter
from ..core.models import (
    ExecutionPlan, TableScan, JoinOperation, 
    IndexSuggestion, DatabaseType, ScanType, ExecutionPlanNode
)

class PostgresAdapter(DatabaseAdapter):
    """PostgreSQL-specific implementation"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def connect(self) -> None:
        self._connection = psycopg2.connect(self.connection_string)
        self._cursor = self._connection.cursor()
    
    def execute_ddl(self, ddl_query: str) -> None:
        """Execute a DDL query."""
        self._cursor.execute(ddl_query)
        self._connection.commit()


    
    def explain_query(self, query: str, analyze: bool = True) -> ExecutionPlan:
        """Run EXPLAIN ANALYZE and parse results"""
        if ';' in query.strip()[:-1]:
            raise ValueError("Multi-statement queries are not allowed.")

        explain_cmd = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)" if analyze else "EXPLAIN (FORMAT JSON)"
        
        self._cursor.execute(f"{explain_cmd} {query}")
        raw_plan_result = self._cursor.fetchone()
        # raw_plan_result is typically a tuple like ([{'Plan': {...}}],)
        # We need to extract the dictionary from within the list
        if raw_plan_result and isinstance(raw_plan_result[0], list) and raw_plan_result[0]:
            raw_plan_dict = raw_plan_result[0][0]
        else:
            raw_plan_dict = {} # Handle cases where plan is empty or unexpected format
        
        # print(f"DEBUG Raw plan: {json.dumps(raw_plan_dict, indent=2)}")
        return self._parse_postgres_plan(raw_plan_dict)
    
        
    
    def _parse_postgres_plan(self, raw_plan: Dict[str, Any]) -> ExecutionPlan:
        """Convert PostgreSQL plan to universal ExecutionPlan"""
        table_scans = []
        joins = []
        warnings = []
        
        def get_table_name_from_node(node: Dict[str, Any]) -> Optional[str]:
            """Recursively find the first table name in a plan branch."""
            if 'Relation Name' in node:
                return node.get('Schema', 'public') + '.' + node['Relation Name']
            for child in node.get('Plans', []):
                name = get_table_name_from_node(child)
                if name:
                    return name
            return None

        def traverse_plan(node: Dict[str, Any]):
            node_type = node.get('Node Type', '')
            
            # Detect table scans
            if 'Scan' in node_type:
                scan_type = self._map_scan_type(node_type)
                table_name = node.get('Relation Name', 'unknown')
                
                table_scans.append(TableScan(
                    table_name=table_name,
                    scan_type=scan_type,
                    rows_examined=node.get('Rows Removed by Filter', 0) + node.get('Actual Rows', 0),
                    rows_returned=node.get('Actual Rows', 0),
                    cost=node.get('Total Cost', 0),
                    time_ms=node.get('Actual Total Time', 0),
                    filter_conditions=self._extract_filters(node)
                ))
                
                # Flag sequential scans on large tables
                if scan_type == ScanType.SEQUENTIAL and node.get('Actual Rows', 0) > 10000:
                    warnings.append(f"Sequential scan on '{table_name}' returned {node.get('Actual Rows')} rows. This might be inefficient.")
            
            # Detect joins
            elif node_type in ['Nested Loop', 'Hash Join', 'Merge Join']:
                left_table = get_table_name_from_node(node['Plans'][0]) if 'Plans' in node and len(node['Plans']) > 0 else 'unknown'
                right_table = get_table_name_from_node(node['Plans'][1]) if 'Plans' in node and len(node['Plans']) > 1 else 'unknown'
                
                joins.append(JoinOperation(
                    join_type=node_type.lower().replace(' ', '_'),
                    left_table=left_table,
                    right_table=right_table,
                    condition=node.get('Join Filter', node.get('Hash Cond', '')),
                    rows_examined=node.get('Actual Rows', 0),
                    cost=node.get('Total Cost', 0)
                ))
            
            # Recursively process child nodes
            for child in node.get('Plans', []):
                traverse_plan(child)
        
        plan_tree = raw_plan[0].get('Plan', {}) if isinstance(raw_plan, list) else raw_plan.get('Plan', {})
        traverse_plan(plan_tree)

        # print(f"DEBUG: Found {len(table_scans)} table scans, {len(joins)} joins")
        
        
        return ExecutionPlan(
            query_text="",  
            adapter_name="postgres",  
            execution_time_ms=raw_plan[0].get('Execution Time', 0) / 1000 if isinstance(raw_plan, list) else raw_plan.get('Execution Time', 0) / 1000,
            root_node=ExecutionPlanNode(node_type="Root", cost=plan_tree.get('Total Cost', 0), rows=0), 
            database_type=DatabaseType.POSTGRES,
            total_cost=plan_tree.get('Total Cost', 0),
            table_scans=table_scans,
            joins=joins,
            warnings=warnings,
            raw_plan=raw_plan
        )
    
    def _map_scan_type(self, pg_scan_type: str) -> ScanType:
        """Map PostgreSQL scan types to universal enum"""
        mapping = {
            'Seq Scan': ScanType.SEQUENTIAL,
            'Index Scan': ScanType.INDEX,
            'Index Only Scan': ScanType.INDEX_ONLY,
            'Bitmap Heap Scan': ScanType.BITMAP,
            'Bitmap Index Scan': ScanType.BITMAP
        }
        return mapping.get(pg_scan_type, ScanType.SEQUENTIAL)
    
    def _extract_filters(self, node: Dict[str, Any]) -> List[str]:
        """Extract filter conditions from plan node"""
        filters = []
        if 'Filter' in node:
            filters.append(node['Filter'])
        if 'Index Cond' in node:
            filters.append(node['Index Cond'])
        return filters
    
    def suggest_indexes(self, plan: ExecutionPlan) -> List[IndexSuggestion]:
        suggestions = []
        
        for scan in plan.table_scans:
            # Suggest indexes for costly sequential scans with filters
            if scan.scan_type == ScanType.SEQUENTIAL and scan.rows_examined > 1000 and scan.filter_conditions:
                # Extract columns using regex for PostgreSQL filter format
                columns = set()
                
                for condition in scan.filter_conditions:
                    # Matches column names before operators in PostgreSQL filters
                    matches = re.findall(r'(\w+)\s*[><=]', condition)
                    columns.update(matches)
                
                columns = list(columns)
                
                if columns:
                    # Estimate improvement based on rows examined vs returned
                    reduction = scan.rows_examined - scan.rows_returned
                    improvement = (reduction / scan.rows_examined) * 100 if scan.rows_examined > 0 else 0
                    
                    suggestions.append(IndexSuggestion(
                        table_name=scan.table_name,
                        columns=columns,
                        index_type='btree',
                        estimated_improvement=min(improvement, 99.0),
                        rationale=f"A sequential scan on '{scan.table_name}' examined {scan.rows_examined} rows but only returned {scan.rows_returned}. "
                                f"Adding an index on the filtered column(s) ({', '.join(columns)}) should significantly reduce I/O.",
                        create_statement=f"CREATE INDEX idx_{scan.table_name}_{'_'.join(columns)} ON {scan.table_name} ({', '.join(columns)});"
                    ))
        
        return suggestions

    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Execute a query and return all results."""
        self._cursor.execute(query, params or ())
        return self._cursor.fetchall()

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get PostgreSQL table statistics"""
        query = """
            SELECT 
                pg_stat_user_tables.n_live_tup as row_count,
                pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                n_tup_ins + n_tup_upd + n_tup_del as write_activity
            FROM pg_stat_user_tables
            WHERE relname = %s
        """
        result = self.execute_query(query, (table_name,))
        return {
            'row_count': result[0][0] if result else 0,
            'total_size': result[0][1] if result else 'unknown',
            'write_activity': result[0][2] if result else 0
        }
    
    def _extract_columns_from_conditions(self, conditions: List[str]) -> List[str]:
        """Parse column names from WHERE conditions using sqlparse."""
        columns = set()
        for condition in conditions:
            # The condition from EXPLAIN is not a full query, so we wrap it
            parsed = sqlparse.parse(f"SELECT * FROM t WHERE {condition}")
            if not parsed:
                continue
            
            # Find all identifiers that are not functions
            for token in parsed[0].tokens:
                if isinstance(token, sqlparse.sql.Where):
                    for item in token.tokens:
                        if isinstance(item, sqlparse.sql.Comparison):
                            # Extract identifiers from the comparison
                            for comp_token in item.tokens:
                                if isinstance(comp_token, sqlparse.sql.Identifier):
                                    columns.add(comp_token.get_real_name())
        return sorted(list(columns))
    
    def estimate_query_cost(self, query: str) -> float:
        """Get cost estimate without running query"""
        if ';' in query.strip()[:-1]:
            raise ValueError("Multi-statement queries are not allowed.")
        self._cursor.execute(f"EXPLAIN (FORMAT JSON) {query}")
        plan = self._cursor.fetchone()[0][0]
        return plan['Plan']['Total Cost']
    
    def validate_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate PostgreSQL query syntax"""
        if ';' in query.strip()[:-1]:
            return False, "Multi-statement queries are not allowed."
        try:
            self._cursor.execute(f"EXPLAIN {query}")
            self._connection.rollback()
            return True, None
        except psycopg2.Error as e:
            self._connection.rollback()
            return False, str(e)

    def get_slow_queries(self, min_mean_time_ms: float = 10.0) -> List[Dict[str, Any]]:
        """
        Fetches slow queries from pg_stat_statements.
        Requires the pg_stat_statements extension to be enabled.
        """
        query = """
            SELECT
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time >= %s
            ORDER BY mean_exec_time DESC
            LIMIT 50;
        """
        try:
            return self.execute_query(query, (min_mean_time_ms,))
        except psycopg2.Error as e:
            if 'relation "pg_stat_statements" does not exist' in str(e):
                raise ConnectionError(
                    "The 'pg_stat_statements' extension is not enabled on your PostgreSQL server. "
                    "Please run 'CREATE EXTENSION IF NOT EXISTS pg_stat_statements;' as a superuser."
                ) from e
            raise e

    def get_table_schema(self, table_name: str) -> str:
        """Retrieves the CREATE TABLE statement for a given table."""
        # This is a simplified version. A more robust solution is complex.
        query = f"""
        SELECT 'CREATE TABLE ' || '{table_name}' || ' (' ||
            string_agg(column_name || ' ' || data_type, ', '),
            ')'
        FROM information_schema.columns
        WHERE table_name = '{table_name.split('.')[-1]}';
        """
        try:
            result = self.execute_query(query)
            return result[0][0] if result and result[0] else f"-- Could not retrieve schema for {table_name}"
        except Exception:
            return f"-- Error retrieving schema for {table_name}"
        
    def close(self):
        if self._connection:
            self._connection.close()  # THIS LINE triggers the mock
            self._connection = None