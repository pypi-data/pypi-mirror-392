# src/query_optimizer/adapters/sqlite.py
import sqlite3
import re
from typing import Dict, Any, List, Optional, Tuple
from ..core.analyzer import DatabaseAdapter
import sqlparse
from ..core.models import (
    ExecutionPlan, TableScan, JoinOperation,
    IndexSuggestion, DatabaseType, ScanType, ExecutionPlanNode
)

class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter - simpler but educational"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def connect(self) -> None:
        # Extract db path from connection string
        db_path = self.connection_string.replace('sqlite:///', '')
        self._connection = sqlite3.connect(db_path)
        self._cursor = self._connection.cursor()

    def execute_ddl(self, ddl_query: str) -> None:
        """Execute a DDL query."""
        self._cursor.execute(ddl_query)
        self._connection.commit()

    
    def explain_query(self, query: str, analyze: bool = True) -> ExecutionPlan:
        """SQLite EXPLAIN QUERY PLAN"""
        self._cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        rows = self._cursor.fetchall()
        
        return self._parse_sqlite_plan(rows, query)
    
    def _parse_sqlite_plan(self, plan_rows: List, query: str) -> ExecutionPlan:
        """Parse SQLite's simpler output"""
        table_scans = []
        warnings = []
        
        for row in plan_rows:
            detail = row[3] if len(row) > 3 else str(row)
            
            if 'SCAN' in detail:
                # Extract table name
                table_match = re.search(r'SCAN (\w+)', detail)
                table_name = table_match.group(1) if table_match else 'unknown'
                
                # Check if using index
                using_index = 'USING INDEX' in detail
                
                table_scans.append(TableScan(
                    table_name=table_name,
                    scan_type=ScanType.INDEX if using_index else ScanType.SEQUENTIAL,
                    rows_examined=0,  # SQLite doesn't provide this
                    rows_returned=0,
                    cost=0,
                    time_ms=0,
                    filter_conditions=[]
                ))
                
                if not using_index:
                    warnings.append(f"Full table scan on {table_name}")
        
        return ExecutionPlan(
            query_text=query,  # Use the actual query
            adapter_name=DatabaseType.SQLITE.value,
            root_node=ExecutionPlanNode(node_type="Unknown", cost=0.0, rows=0), # Placeholder
            database_type=DatabaseType.SQLITE,
            total_cost=0,
            table_scans=table_scans,
            joins=[],
            warnings=warnings,
            raw_plan={'rows': plan_rows}
        )
    
    def suggest_indexes(self, plan: ExecutionPlan) -> List[IndexSuggestion]:
        """SQLite index suggestions"""
        suggestions = []
        
        for scan in plan.table_scans:
            if scan.scan_type == ScanType.SEQUENTIAL:
                # Parse WHERE clause from query to guess columns
                # This is simplified - real version would use sqlparse
                columns = self._extract_columns_from_query(plan.query_text)
                if not columns:
                    columns = ['id']  # fallback
                    
                suggestions.append(IndexSuggestion(
                    table_name=scan.table_name,
                    columns=columns,
                    index_type='',
                    estimated_improvement=50.0,
                    rationale=f"Sequential scan detected on {scan.table_name}",
                    create_statement=f"CREATE INDEX idx_{scan.table_name}_{'_'.join(columns)} ON {scan.table_name} ({', '.join(columns)});"
                ))

        return suggestions
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Execute a query and return all results."""
        self._cursor.execute(query, params or ())
        return self._cursor.fetchall()

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Basic SQLite stats"""
        self._cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = self._cursor.fetchone()[0]
        
        return {
            'row_count': count,
            'total_size': 'N/A',
            'indexes': []
        }
    
    def estimate_query_cost(self, query: str) -> float:
        """SQLite doesn't provide cost estimates"""
        return 0.0
    
    def validate_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate SQLite syntax"""
        try:
            self._cursor.execute(f"EXPLAIN {query}")
            return True, None
        except sqlite3.Error as e:
            return False, str(e)
        
    def close(self):
        if self._connection:
            self._connection.close()  # THIS LINE triggers the mock
            self._connection = None

    def _extract_columns_from_query(self, query: str) -> List[str]:
  
    
    
        parsed = sqlparse.parse(query)
        if not parsed:
            return []
        
        columns = []
        for token in parsed[0].tokens:
            if isinstance(token, sqlparse.sql.Where):
                # Walk through WHERE clause tokens
                for item in token.flatten():
                    if item.ttype is sqlparse.tokens.Name:
                        # Skip operator words and values
                        if item.value.lower() not in ('and', 'or', 'not', 'in', 'like'):
                            columns.append(item.value)
        
        return list(dict.fromkeys(columns))  # Remove duplicates
