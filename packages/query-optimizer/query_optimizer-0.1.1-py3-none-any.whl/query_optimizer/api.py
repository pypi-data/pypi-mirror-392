from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
import re
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceede

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["3 per day"]
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app = FastAPI(
    title="Query Optimizer API",
    description="Analyze SQL queries and get optimization suggestions without touching your data",
    version="1.0.0"
)

# Allow CORS for web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    database_type: Optional[str] = "postgresql"  # postgresql, mysql, sqlite

class IndexSuggestion(BaseModel):
    table: str
    columns: List[str]
    index_name: str
    create_statement: str
    reason: str
    estimated_improvement: str

class OptimizationResponse(BaseModel):
    original_query: str
    suggestions: List[IndexSuggestion]
    warnings: List[str]
    benchmark_script: str

def extract_tables_columns(query: str):
    """Extract tables and columns from WHERE clauses"""
    parsed = sqlparse.parse(query)[0]
    tables = []
    where_columns = {}
    
    # Find tables
    from_seen = False
    for token in parsed.tokens:
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
            from_seen = True
        elif from_seen and isinstance(token, Identifier):
            tables.append(token.get_real_name())
        elif isinstance(token, IdentifierList):
            for ident in token.get_identifiers():
                tables.append(ident.get_real_name())
                
    # Find WHERE conditions
    for token in parsed.tokens:
        if isinstance(token, Where):
            for item in token.tokens:
                if isinstance(item, Comparison):
                    # Extract column name (left side of comparison)
                    col_token = item.left
                    if hasattr(col_token, 'value'):
                        col = col_token.value.strip()
                        # Remove table prefix if exists
                        if '.' in col:
                            table, col = col.split('.', 1)
                        else:
                            table = tables[0] if tables else 'unknown'
                        
                        if table not in where_columns:
                            where_columns[table] = []
                        if col not in where_columns[table]:
                            where_columns[table].append(col)
    
    return tables, where_columns

def analyze_query_patterns(query: str, db_type: str):
    """Analyze query for common performance patterns"""
    suggestions = []
    warnings = []
    
    query_upper = query.upper()
    tables, where_columns = extract_tables_columns(query)
    
    # Pattern 1: SELECT * - always bad for performance
    if 'SELECT *' in query_upper:
        warnings.append("SELECT * fetches unnecessary columns, slowing down queries")
    
    # Pattern 2: Missing indexes on WHERE columns
    for table, columns in where_columns.items():
        if columns:
            index_name = f"idx_{table}_{'_'.join(columns)}"
            create_stmt = f"CREATE INDEX {index_name} ON {table} ({', '.join(columns)})"
            
            suggestions.append(IndexSuggestion(
                table=table,
                columns=columns,
                index_name=index_name,
                create_statement=create_stmt,
                reason=f"WHERE clause filters on {', '.join(columns)} without an index",
                estimated_improvement="10-100x faster for large tables"
            ))
    
    # Pattern 3: LIKE with leading wildcard
    if re.search(r"LIKE\s+['\"]%", query_upper):
        warnings.append("LIKE '%text' cannot use indexes. Consider full-text search.")
    
    # Pattern 4: Multiple JOINs without indexes
    join_count = query_upper.count('JOIN')
    if join_count > 2:
        warnings.append(f"Query has {join_count} JOINs. Ensure foreign keys are indexed.")
    
    return suggestions, warnings

def generate_benchmark_script(query: str, suggestions: List[IndexSuggestion], db_type: str):
    """Generate a script users can run on their own database"""
    
    if db_type == "postgresql":
        conn_example = "psycopg2.connect('your_connection_string')"
        explain = "EXPLAIN (ANALYZE, BUFFERS)"
    elif db_type == "mysql":
        conn_example = "mysql.connector.connect(**your_config)"
        explain = "EXPLAIN"
    else:
        conn_example = "sqlite3.connect('your_database.db')"
        explain = "EXPLAIN QUERY PLAN"
    
    script = f'''#!/usr/bin/env python3
"""
Query Optimization Benchmark Script
Generated by Query Optimizer API
"""
import time
import {db_type}

# Connect to YOUR database
conn = {conn_example}
cursor = conn.cursor()

print("🔍 Analyzing current query performance...")
print("Query: {query[:100]}...")

# Measure BEFORE optimization
cursor.execute("{explain} {query}")
before_plan = cursor.fetchall()
print("\\n📊 Current execution plan:")
for row in before_plan:
    print(row)

start = time.time()
cursor.execute("{query}")
results = cursor.fetchall()
before_time = time.time() - start
print(f"\\n⏱️  Current execution time: {{before_time:.3f}} seconds")
print(f"📊 Rows returned: {{len(results)}}")

# Apply optimizations
print("\\n🔧 Applying optimizations...")
'''

    for i, suggestion in enumerate(suggestions, 1):
        script += f'''
print(f"{{i}}. Creating index: {suggestion.index_name}")
try:
    cursor.execute("{suggestion.create_statement}")
    conn.commit()
    print("   ✅ Index created successfully")
except Exception as e:
    print(f"   ⚠️  Index may already exist: {{e}}")
'''

    script += f'''
# Measure AFTER optimization
print("\\n📈 Testing optimized query...")
cursor.execute("{explain} {query}")
after_plan = cursor.fetchall()
print("\\nOptimized execution plan:")
for row in after_plan:
    print(row)

start = time.time()
cursor.execute("{query}")
results = cursor.fetchall()
after_time = time.time() - start

# Show results
print(f"\\n🎯 RESULTS:")
print(f"Before optimization: {{before_time:.3f}} seconds")
print(f"After optimization:  {{after_time:.3f}} seconds")
if after_time > 0:
    print(f"\\n🚀 {{before_time/after_time:.1f}}x faster!")
else:
    print(f"\\n🚀 Near-instant execution!")

cursor.close()
conn.close()
'''
    return script

@app.get("/")
async def root():
    return {
        "message": "Query Optimizer API",
        "endpoints": {
            "/analyze": "POST - Analyze a SQL query",
            "/docs": "GET - Interactive API documentation"
        }
    }

@app.post("/analyze", response_model=OptimizationResponse)
@limiter.limit("3 per day")
async def analyze(request: Request, query_request: QueryRequest):
    """Analyze SQL query structure and suggest optimizations"""
    try:
        suggestions, warnings = analyze_query_patterns(request.query, request.database_type)
        benchmark_script = generate_benchmark_script(request.query, suggestions, request.database_type)
        
        return OptimizationResponse(
            original_query=request.query,
            suggestions=suggestions,
            warnings=warnings,
            benchmark_script=benchmark_script
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query analysis failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy"}
