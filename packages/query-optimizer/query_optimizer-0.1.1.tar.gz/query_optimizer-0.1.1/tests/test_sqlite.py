import pytest
from unittest.mock import patch, MagicMock
from query_optimizer.adapters.sqlite import SQLiteAdapter
from query_optimizer.core.models import ExecutionPlan, ExecutionPlanNode
import sqlite3

# NOTE: This file focuses on basic SQLite connection and the QUERY PLAN command.

@patch('query_optimizer.adapters.sqlite.sqlite3.connect', return_value=MagicMock(close=MagicMock()))
def test_sqlite_adapter_connect_close(mock_connect):
    """Tests successful connection and closure."""
    adapter = SQLiteAdapter(connection_string="sqlite:///test.db")
    adapter.connect()
    mock_connect.assert_called_once_with('test.db')
    mock_conn = adapter._connection
    adapter.close()
    mock_conn.close.assert_called_once()

    

@patch('query_optimizer.adapters.sqlite.sqlite3.connect', side_effect=sqlite3.Error("File not found"))
def test_sqlite_adapter_connect_failure(mock_connect):
    """Tests connection failure and exception handling."""
    adapter = SQLiteAdapter(connection_string="sqlite:///test.db")
    with pytest.raises(sqlite3.Error, match="File not found"):
        adapter.connect()

@patch('query_optimizer.adapters.sqlite.sqlite3.connect')
def test_get_execution_plan_success(mock_connect):
    """Tests execution of EXPLAIN QUERY PLAN and basic node parsing."""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (0, 0, 0, 'SCAN users'),
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    adapter = SQLiteAdapter(connection_string="sqlite:///test.db")
    adapter.connect()
    plan = adapter.explain_query("SELECT 1;")
    
    mock_cursor.execute.assert_called_once()
    assert "EXPLAIN QUERY PLAN" in mock_cursor.execute.call_args[0][0]
    
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.table_scans) == 1
    assert plan.table_scans[0].table_name == "users"
