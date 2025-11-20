# src/query_optimizer/adapters/mysql.py
import mysql.connector
import json
from typing import Dict, Any, List, Optional, Tuple
from ..core.analyzer import DatabaseAdapter
from ..core.models import (
    ExecutionPlan, TableScan, JoinOperation,
    IndexSuggestion, DatabaseType, ScanType, ExecutionPlanNode
)
from unittest.mock import MagicMock

class MySQLAdapter(DatabaseAdapter):
    """MySQL-specific implementation"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def _parse_connection_string(self) -> Dict[str, str]:
        """Parses the connection string into a dictionary."""
        params = {}
        for part in self.connection_string.split(' '):
            key, value = part.split('=')
            params[key] = value
        return params

    def connect(self) -> None:
        # Parse connection string for mysql
        # Fix: Ensure self._connection is the mock's return value if mysql.connector.connect is mocked.
        self._connection = mysql.connector.connect(**self._parse_connection_string())

        self._cursor = self._connection.cursor(dictionary=True)
    
    def explain_query(self, query: str, analyze: bool = True) -> ExecutionPlan:
        """MySQL EXPLAIN FORMAT=JSON"""
        self._cursor.execute(f"EXPLAIN FORMAT=JSON {query}")
        raw_plan = json.loads(self._cursor.fetchone()['EXPLAIN'])
        
        return self._parse_mysql_plan(raw_plan)
    
    def _parse_mysql_plan(self, raw_plan: Dict[str, Any]) -> ExecutionPlan:
        """Convert MySQL plan to universal format"""
        query_block = raw_plan.get('query_block', {})
        table_scans = []
        joins = []
        warnings = []
        
        # MySQL structures plans differently than PostgreSQL
        if 'table' in query_block:
            # Single table query
            table = query_block['table']
            table_scans.append(self._parse_table_access(table))
        elif 'nested_loop' in query_block:
            # Join query
            for table in query_block['nested_loop']:
                if 'table' in table:
                    table_scans.append(self._parse_table_access(table['table']))
        
        # Check for missing indexes
        cost_info = query_block.get('cost_info', {})
        if 'read_cost' in cost_info and cost_info['read_cost'] > 1000:
            warnings.append("High read cost detected - consider adding indexes")
        
        return ExecutionPlan(
            query_text="",  # Placeholder
            adapter_name=DatabaseType.MYSQL.value,
            root_node=ExecutionPlanNode(node_type="Unknown", cost=0.0, rows=0), # Placeholder
            database_type=DatabaseType.MYSQL,
            total_cost=float(cost_info.get('query_cost', 0)),
            table_scans=table_scans,
            joins=joins,
            warnings=warnings,
            raw_plan=raw_plan
        )
    
    def _parse_table_access(self, table_info: Dict[str, Any]) -> TableScan:
        """Parse MySQL table access info"""
        access_type = table_info.get('access_type', 'ALL')
        
        scan_type_map = {
            'ALL': ScanType.SEQUENTIAL,
            'index': ScanType.INDEX,
            'range': ScanType.INDEX,
            'ref': ScanType.INDEX,
            'const': ScanType.INDEX
        }
        
        return TableScan(
            table_name=table_info.get('table_name', ''),
            scan_type=scan_type_map.get(access_type, ScanType.SEQUENTIAL),
            rows_examined=int(table_info.get('rows_examined_per_scan', 0)),
            rows_returned=int(table_info.get('rows_produced_per_join', 0)),
            cost=float(table_info.get('cost_info', {}).get('read_cost', 0)),
            time_ms=0,
            filter_conditions=[table_info.get('attached_condition', '')]
        )
    
    def suggest_indexes(self, plan: ExecutionPlan) -> List[IndexSuggestion]:
        """MySQL-specific index suggestions"""
        suggestions = []
        import re
        
        for scan in plan.table_scans:
            if scan.scan_type == ScanType.SEQUENTIAL and scan.rows_examined > 1000 and scan.filter_conditions:
                # Extract columns using regex for MySQL filter format
                columns = []
                seen = set()
                
                for condition in scan.filter_conditions:
                    if condition:  # Skip empty conditions
                        # Match column names before operators
                        matches = re.findall(r'`?(\w+)`?\s*[><=]', condition)
                        for match in matches:
                            if match not in seen:
                                columns.append(match)
                                seen.add(match)
                
                if columns:
                    # Estimate improvement based on rows examined vs returned
                    reduction = scan.rows_examined - scan.rows_returned
                    improvement = (reduction / scan.rows_examined) * 100 if scan.rows_examined > 0 else 0
                    
                    suggestions.append(IndexSuggestion(
                        table_name=scan.table_name,
                        columns=columns,
                        index_type='BTREE',
                        estimated_improvement=min(improvement, 99.0),
                        rationale=f"Table scan on {scan.table_name} examined {scan.rows_examined} rows but only returned {scan.rows_returned}. "
                                f"Adding an index on ({', '.join(columns)}) should reduce I/O.",
                        create_statement=f"ALTER TABLE {scan.table_name} ADD INDEX idx_{scan.table_name}_{'_'.join(columns)} ({', '.join(columns)});"
                    ))
        
        return suggestions

    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Execute a query and return all results."""
        self._cursor.execute(query, params or ())
        return self._cursor.fetchall()

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get MySQL table statistics"""
        self._cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
        stats = self._cursor.fetchone()
        
        return {
            'row_count': stats['Rows'] if stats else 0,
            'total_size': f"{stats['Data_length'] / 1024 / 1024:.2f} MB" if stats else 'unknown',
            'index_size': f"{stats['Index_length'] / 1024 / 1024:.2f} MB" if stats else 'unknown'
        }
    
    def estimate_query_cost(self, query: str) -> float:
        """Estimate query cost from EXPLAIN"""
        self._cursor.execute(f"EXPLAIN FORMAT=JSON {query}")
        plan = json.loads(self._cursor.fetchone()['EXPLAIN'])
        return float(plan.get('query_block', {}).get('cost_info', {}).get('query_cost', 0))

    
    def validate_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate MySQL syntax"""
        try:
            # Create temp connection to test query
            self._cursor.execute(f"EXPLAIN {query}")
            self._cursor.fetchall()
            return True, None
        except mysql.connector.Error as e:
            return False, str(e)

    def execute_ddl(self, ddl_query: str) -> None:
        """Execute a DDL query."""
        self._cursor.execute(ddl_query)
        self._connection.commit()


    def close(self):
        if self._connection:
            self._connection.close()  # THIS LINE triggers the mock
            self._connection = None

