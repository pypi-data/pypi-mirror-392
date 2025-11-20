import pytest
from unittest.mock import patch, MagicMock
from query_optimizer.adapters.postgres import PostgresAdapter
from query_optimizer.core.models import ExecutionPlan, ExecutionPlanNode
import psycopg2

# NOTE: This file uses fixtures from tests/conftest.py

@patch('query_optimizer.adapters.postgres.psycopg2.connect', return_value=MagicMock(close=MagicMock()))
def test_postgres_adapter_connect_close(mock_connect):
    """Tests successful connection and closure."""
    adapter = PostgresAdapter(connection_string="dbname=test")
    adapter.connect()
    mock_connect.assert_called_once_with("dbname=test")
    
    mock_conn = adapter._connection  # Save it
    adapter.close()
    mock_conn.close.assert_called_once()


@patch('query_optimizer.adapters.postgres.psycopg2.connect', side_effect=psycopg2.Error("Auth failed"))
def test_postgres_adapter_connect_failure(mock_connect):
    """Tests connection failure and exception handling."""
    adapter = PostgresAdapter(connection_string="dbname=test")
    with pytest.raises(psycopg2.Error, match="Auth failed"):
        adapter.connect()
    mock_connect.assert_called_once_with("dbname=test")

def test_postgres_adapter_connect_not_called():
    """Tests that adapter methods fail if connect() was not called."""
    adapter = PostgresAdapter(connection_string="dbname=test")
    with pytest.raises(AttributeError):
        adapter.explain_query("SELECT 1;")
    with pytest.raises(AttributeError):
        adapter.get_slow_queries()

@patch('query_optimizer.adapters.postgres.psycopg2.connect')
def test_get_execution_plan_success(mock_connect, mock_postgres_explain_json):
    """Tests successful execution of EXPLAIN and correct plan parsing."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [mock_postgres_explain_json]
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    adapter = PostgresAdapter(connection_string="dbname=test")
    adapter.connect()
    plan = adapter.explain_query("SELECT 1;")
    
    mock_cursor.execute.assert_called_once()
    assert "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)" in mock_cursor.execute.call_args[0][0]
    
    assert isinstance(plan, ExecutionPlan)
    assert plan.total_cost == 50000.0
    assert plan.execution_time_ms == 0.1505
    assert len(plan.table_scans) == 1
    assert plan.table_scans[0].table_name == "users"

@patch('query_optimizer.adapters.postgres.psycopg2.connect')
def test_get_execution_plan_query_error(mock_connect):
    """Tests error handling when the database rejects the query."""
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = psycopg2.Error("Bad SQL")
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    adapter = PostgresAdapter(connection_string="dbname=test")
    adapter.connect()
    with pytest.raises(psycopg2.Error, match="Bad SQL"):
        adapter.explain_query("SELECT BAD_SQL;")

@patch('query_optimizer.adapters.postgres.psycopg2.connect')
def test_get_slow_queries_success(mock_connect, mock_postgres_slow_queries):
    """Tests successful retrieval of slow query metrics."""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_postgres_slow_queries
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    adapter = PostgresAdapter(connection_string="dbname=test")
    adapter.connect()
    metrics = adapter.get_slow_queries(min_mean_time_ms=10.0)
    
    mock_cursor.execute.assert_called_once()
    assert "FROM pg_stat_statements" in mock_cursor.execute.call_args[0][0]
    
    assert isinstance(metrics, list)

@patch('query_optimizer.adapters.postgres.psycopg2.connect')
def test_get_slow_queries_pg_stat_statements_missing(mock_connect):
    """Tests graceful failure when pg_stat_statements is not installed."""
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = psycopg2.Error('relation "pg_stat_statements" does not exist')
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    adapter = PostgresAdapter(connection_string="dbname=test")
    adapter.connect()
    with pytest.raises(ConnectionError, match="The 'pg_stat_statements' extension is not enabled"):
        adapter.get_slow_queries()
