"""
Tests for client query functionality.
"""
import pytest
from database.queries import clients as client_queries

def test_get_all_clients():
    """
    Test that get_all_clients returns a list of clients.
    """
    clients = client_queries.get_all_clients()
    assert isinstance(clients, list), "Clients should be a list"
    
    # Skip further tests if no clients are found
    if not clients:
        pytest.skip("No clients found in database")
    
    # Verify structure of first client
    client = clients[0]
    assert 'client_id' in client, "Client should have client_id"
    assert 'display_name' in client, "Client should have display_name"

def test_get_clients_by_provider():
    """
    Test that get_clients_by_provider returns clients grouped by provider.
    """
    clients = client_queries.get_clients_by_provider()
    assert isinstance(clients, list), "Result should be a list"
    
    # Skip further tests if no clients are found
    if not clients:
        pytest.skip("No clients found in database")
    
    # Verify structure of first client group
    client = clients[0]
    assert 'provider_name' in client, "Client should have provider_name"

def test_get_client_by_id(test_client_id):
    """
    Test that get_client_by_id returns a single client.
    """
    client = client_queries.get_client_by_id(test_client_id)
    assert client is not None, "Client should not be None"
    assert client['client_id'] == test_client_id, "Client ID should match requested ID"
    assert 'display_name' in client, "Client should have display_name"

def test_get_client_with_contracts(test_client_id):
    """
    Test that get_client_with_contracts returns a client with contracts.
    """
    client = client_queries.get_client_with_contracts(test_client_id)
    assert client is not None, "Client should not be None"
    assert client['client_id'] == test_client_id, "Client ID should match requested ID"
    assert 'contracts' in client, "Client should have contracts list"
    
    # Contracts may be empty, but should be a list
    assert isinstance(client['contracts'], list), "Contracts should be a list"

def test_get_client_metrics(test_client_id):
    """
    Test that get_client_metrics returns metrics for a client.
    """
    metrics = client_queries.get_client_metrics(test_client_id)
    # Metrics might be None if no data exists
    if metrics is not None:
        assert metrics['client_id'] == test_client_id, "Metrics client_id should match requested ID"

def test_get_client_compliance_status(test_client_id):
    """
    Test that get_client_compliance_status returns a compliance status.
    """
    status = client_queries.get_client_compliance_status(test_client_id)
    assert isinstance(status, dict), "Status should be a dictionary"
    assert 'status' in status, "Status should have a status field"
    assert 'reason' in status, "Status should have a reason field"

def test_get_quarterly_summary(test_client_id):
    """
    Test that get_quarterly_summary returns a quarterly summary if it exists.
    """
    # Use a common year/quarter for testing
    year = 2023
    quarter = 1
    
    summary = client_queries.get_quarterly_summary(test_client_id, year, quarter)
    # Summary might be None if no data exists for that quarter
    if summary is not None:
        assert summary['client_id'] == test_client_id, "Summary client_id should match requested ID"
        assert summary['year'] == year, "Summary year should match requested year"
        assert summary['quarter'] == quarter, "Summary quarter should match requested quarter"

def test_get_yearly_summary(test_client_id):
    """
    Test that get_yearly_summary returns a yearly summary if it exists.
    """
    # Use a common year for testing
    year = 2023
    
    summary = client_queries.get_yearly_summary(test_client_id, year)
    # Summary might be None if no data exists for that year
    if summary is not None:
        assert summary['client_id'] == test_client_id, "Summary client_id should match requested ID"
        assert summary['year'] == year, "Summary year should match requested year"