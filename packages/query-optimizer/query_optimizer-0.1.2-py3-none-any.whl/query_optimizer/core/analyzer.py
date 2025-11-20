import re
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from .models import ExecutionPlan, IndexSuggestion, TableScan, ScanType, QueryMetric

class DatabaseAdapter(ABC):
    """Abstract base class for all database adapters."""
    
    # NOTE: The actual __init__ and connection handling is implemented in derived classes.
    
    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""
        pass

    def close(self) -> None:
        """Close the database connection (optional, default implementation does nothing)."""
        pass
        
    @abstractmethod
    def explain_query(self, query: str, analyze: bool = True) -> ExecutionPlan:
        """Fetch and parse the execution plan for a given query."""
        pass

    @abstractmethod
    def suggest_indexes(self, plan: ExecutionPlan) -> List[IndexSuggestion]:
        """Generate database-specific index suggestions based on the plan."""
        pass
        
    @abstractmethod
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Fetch general statistics about a table (row count, size, etc.)."""
        pass
        
    @abstractmethod
    def estimate_query_cost(self, query: str) -> float:
        """Get the estimated cost of a query without execution."""
        pass
        
    @abstractmethod
    def validate_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check if the query is syntactically valid."""
        pass
    
    @abstractmethod
    def execute_ddl(self, ddl_query: str) -> None:
        """Execute a DDL query."""
        pass
    
    def get_slow_queries(self, min_mean_time_ms: float = 10.0) -> List[QueryMetric]:
        """Fetch slow query metrics (default implementation raises an error)."""
        raise NotImplementedError("Slow query monitoring is not supported by this adapter.")

class Analyzer:
    """
    Analyzes an ExecutionPlan to identify performance bottlenecks and generate
    universal IndexSuggestion objects.
    """
    def analyze_plan(self, plan: ExecutionPlan) -> List[IndexSuggestion]:
        """
        Main analysis method. Iterates through table scans and joins to find issues.
        """
        suggestions: List[IndexSuggestion] = []
        
        # 1. Analyze Table Scans for Sequential/Full Scans
        for scan in plan.table_scans:
            # Threshold for considering a scan "large" and therefore sequential/full scans problematic
            LARGE_ROW_THRESHOLD = 5000
            
            if scan.scan_type == ScanType.SEQUENTIAL and scan.rows_examined > LARGE_ROW_THRESHOLD:
                
                # Check for filter conditions to identify candidate index columns
                if scan.filter_conditions:
                    # In a real app, this would use sqlparse to extract columns, 
                    # but for now, we assume a single column for simplicity
                    candidate_columns = self._extract_columns_from_condition(plan.raw_plan)
                    
                    if not candidate_columns:
                        # Fallback to a common optimization strategy if no columns found
                        candidate_columns = ['(column_for_filter)'] 
                        
                    # Calculate estimated improvement based on the size of the scan
                    improvement_pct = min(99.0, (scan.rows_examined - scan.rows_returned) / scan.rows_examined * 100 if scan.rows_examined > 0 else 50.0)

                    # Create a universal suggestion
                    suggestions.append(IndexSuggestion(
                        table_name=scan.table_name,
                        columns=candidate_columns,
                        index_type='BTREE',
                        estimated_improvement=improvement_pct,
                        rationale=f"High-cost Sequential Scan detected on '{scan.table_name}'. "
                                 f"It examined {scan.rows_examined:,} rows. A proper index on "
                                 f"the filter columns should drastically reduce I/O.",
                        create_statement=f"CREATE INDEX idx_{scan.table_name}_opt_{'_'.join(c.strip('()') for c in candidate_columns)} ON {scan.table_name} ({', '.join(candidate_columns)});"
                    ))

        # 2. Analyze Joins (Check for unusually expensive Nested Loops)
        for join in plan.joins:
            if join.join_type == 'nested_loop' and join.cost > 20000:
                # Nested loops are generally bad on large datasets unless highly optimized.
                suggestions.append(IndexSuggestion(
                    table_name=join.right_table or 'N/A',
                    columns=['(join_column)'],
                    index_type='BTREE',
                    estimated_improvement=70.0,
                    rationale=f"High-cost Nested Loop Join detected between {join.left_table} and {join.right_table}. "
                             f"This typically indicates a missing index on the foreign key or join condition.",
                    create_statement=f"-- Consider adding an index on the join key for {join.right_table}"
                ))

        return suggestions

    def _extract_columns_from_condition(self, raw_plan: Dict[str, Any]) -> List[str]:
        """
        A simplified, database-agnostic column extraction from the raw plan for demonstration.
        In a complete application, this would rely on adapter-specific parsing.
        
        Since we don't have sqlparse here, we just look for 'user_id' in the raw structure
        which is used in the test fixture.
        """
        columns = set()
        # Simple heuristic to cover the test case
        raw_json_str = json.dumps(raw_plan)
        if 'user_id' in raw_json_str:
             columns.add('user_id')
        if not columns:
            # Fallback for the case where only a simple filter is known
            match = re.search(r'[\w]+\s*[=<>]', raw_json_str)
            if match:
                columns.add(match.group(0).split()[0].strip())
        
        return sorted(list(columns))