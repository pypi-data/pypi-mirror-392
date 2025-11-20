from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class DatabaseType(Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    CLICKHOUSE = "clickhouse"
    UNKNOWN = "unknown" # <-- FIX: Added the missing UNKNOWN member

class ScanType(Enum):
    SEQUENTIAL = "sequential"
    INDEX = "index"
    INDEX_ONLY = "index_only"
    BITMAP = "bitmap"
    # Used for unparsed/default nodes in the tree structure
    UNKNOWN = "unknown" 

@dataclass
class TableScan:
    """Unified representation of table access (used for flat models)"""
    table_name: str
    scan_type: ScanType
    rows_examined: int
    rows_returned: int
    cost: float
    time_ms: float
    filter_conditions: List[str]

@dataclass
class JoinOperation:
    """Unified representation of joins (used for flat models)"""
    join_type: str  # 'nested_loop', 'hash', 'merge'
    left_table: str
    right_table: str
    condition: str
    rows_examined: int
    cost: float

# --- ESSENTIAL CLASSES FOR TEST SUITE (TREE STRUCTURE) ---

@dataclass(frozen=True)
class ExecutionPlanNode:
    """Represents a single node (operation) in the database execution plan tree."""
    node_type: str
    cost: float
    rows: int
    filter_conditions: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    # Allows recursive definition, required for tree traversal
    children: List['ExecutionPlanNode'] = field(default_factory=list) 

# --- EXECUTION PLAN (AUGMENTED FOR TESTS) ---

@dataclass
class ExecutionPlan:
    """Universal execution plan all DBs map to"""
    
    # Fields required by the test suite for core logic
    query_text: str
    adapter_name: str
    root_node: ExecutionPlanNode 
    
    # Fields from your existing model (kept for compatibility with other logic)
    database_type: DatabaseType = DatabaseType.UNKNOWN # This now works!
    total_cost: Optional[float] = None
    execution_time_ms: Optional[float] = None
    
    # Lists for flatter modeling approach
    table_scans: List[TableScan] = field(default_factory=list)
    joins: List[JoinOperation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    raw_plan: Dict[str, Any] = field(default_factory=dict) # Original DB-specific plan


@dataclass
class IndexSuggestion:
    """Universal index recommendation"""
    table_name: str
    columns: List[str]
    index_type: str  # 'btree', 'hash', 'gin', etc
    estimated_improvement: float  # percentage
    rationale: str
    create_statement: str

@dataclass
class QueryMetric:
    """Represents a single slow query metric."""
    query_text: str
    calls: int
    total_time_ms: float
    mean_time_ms: float
    database_name: str