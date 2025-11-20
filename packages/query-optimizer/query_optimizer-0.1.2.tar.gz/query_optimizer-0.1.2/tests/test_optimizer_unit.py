import pytest
from unittest.mock import patch, MagicMock
from query_optimizer.core.optimizer import Optimizer
from query_optimizer.core.models import IndexSuggestion
from query_optimizer.core.analyzer import DatabaseAdapter

# NOTE: This file uses fixtures from tests/conftest.py

def test_optimizer_init_success():
    """Tests successful initialization of the Optimizer."""
    mock_adapter = MagicMock(spec=DatabaseAdapter)
    optimizer = Optimizer(adapter=mock_adapter)
    assert optimizer.adapter is mock_adapter

def test_get_optimizations_success(mock_postgres_adapter):
    """Tests the full analysis pipeline runs correctly and returns suggestions."""
    optimizer = Optimizer(adapter=mock_postgres_adapter)
    
    # Configure the mock to return a float for estimate_query_cost
    mock_postgres_adapter.estimate_query_cost.return_value = 100.0
    
    suggestions, cost = optimizer.get_optimizations("SELECT * FROM test;")
    
    mock_postgres_adapter.validate_syntax.assert_called_once_with("SELECT * FROM test;")
    mock_postgres_adapter.estimate_query_cost.assert_called_once_with("SELECT * FROM test;")
    mock_postgres_adapter.explain_query.assert_called_once_with("SELECT * FROM test;", analyze=True)
    mock_postgres_adapter.suggest_indexes.assert_called_once()
    
    assert isinstance(suggestions, list)
    assert isinstance(cost, float)

def test_apply_optimizations_success(mock_postgres_adapter):
    """Tests successful application of a generated index suggestion."""
    optimizer = Optimizer(adapter=mock_postgres_adapter)
    suggestion = IndexSuggestion(
        table_name='users', 
        columns=['email'], 
        index_type='btree',
        estimated_improvement=0.0,
        rationale='test',
        create_statement='CREATE INDEX idx_users_email ON users (email);'
    )
    
    optimizer.apply_optimizations([suggestion])
    
    mock_postgres_adapter.execute_ddl.assert_called_once_with('CREATE INDEX idx_users_email ON users (email);')

def test_apply_optimizations_failure(mock_postgres_adapter):
    """Tests failure handling when index creation fails."""
    mock_postgres_adapter.execute_ddl.side_effect = Exception("DB Error")
    optimizer = Optimizer(adapter=mock_postgres_adapter)
    suggestion = IndexSuggestion(
        table_name='users', 
        columns=['email'], 
        index_type='btree',
        estimated_improvement=0.0,
        rationale='test',
        create_statement='CREATE INDEX idx_users_email ON users (email);'
    )
    
    with pytest.raises(Exception, match="DB Error"):
        optimizer.apply_optimizations([suggestion])
