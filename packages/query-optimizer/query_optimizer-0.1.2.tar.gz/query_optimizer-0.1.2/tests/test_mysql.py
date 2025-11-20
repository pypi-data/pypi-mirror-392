import pytest
from unittest.mock import patch, MagicMock
from query_optimizer.adapters.mysql import MySQLAdapter
from query_optimizer.core.models import ExecutionPlan, ExecutionPlanNode
import mysql.connector

# NOTE: This file uses fixtures from tests/conftest.py

@patch('query_optimizer.adapters.mysql.mysql.connector.connect', return_value=MagicMock(close=MagicMock()))
def test_mysql_adapter_connect_close(mock_connect):
    """Tests successful connection and closure."""
    adapter = MySQLAdapter(connection_string="user=root password=pw db=test")
    adapter.connect()
    mock_connect.assert_called_once()

    adapter.close()
    mock_connect.return_value.close.assert_called_once()



@patch('query_optimizer.adapters.mysql.mysql.connector.connect', side_effect=mysql.connector.Error("MySQL Auth Failed"))
def test_mysql_adapter_connect_failure(mock_connect):
    """Tests connection failure and exception handling."""
    adapter = MySQLAdapter(connection_string="user=root password=pw db=test")
    with pytest.raises(mysql.connector.Error, match="MySQL Auth Failed"):
        adapter.connect()

@patch('query_optimizer.adapters.mysql.mysql.connector.connect')
def test_get_execution_plan_success(mock_connect):
    """Tests plan retrieval and parsing logic for MySQL's EXPLAIN format."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {'EXPLAIN': '{"query_block": {"select_id": 1, "cost_info": {"query_cost": "10.0"}, "table": {"table_name": "users", "access_type": "ALL"}}}'}
    mock_connect.return_value.cursor.return_value = mock_cursor
    
    adapter = MySQLAdapter(connection_string="user=root password=pw db=test")
    adapter.connect()
    plan = adapter.explain_query("SELECT 1;")
    
    mock_cursor.execute.assert_called_once()
    assert "EXPLAIN FORMAT=JSON" in mock_cursor.execute.call_args[0][0]
    
    assert isinstance(plan, ExecutionPlan)
    assert plan.total_cost == 10.0
    assert len(plan.table_scans) == 1
    assert plan.table_scans[0].table_name == "users"
