"""
Configuration module for pytest.
Provides fixtures for the test suite.
"""
import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our application modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_db_connection
from database.queries import clients as client_queries
from database.queries import payments as payment_queries
from database.queries import files as file_queries
from services import client_service, payment_service, file_service

@pytest.fixture
def db_connection():
    """
    Fixture that provides a database connection.
    This connection is closed after the test completes.
    """
    conn = get_db_connection()
    yield conn
    conn.close()

@pytest.fixture
def test_client_id():
    """
    Fixture that provides an ID of an existing client for testing.
    """
    # Get first client from database
    clients = client_queries.get_all_clients()
    if not clients:
        pytest.skip("No clients found in database for testing")
    
    return clients[0]['client_id']

@pytest.fixture
def test_contract_id(test_client_id):
    """
    Fixture that provides an ID of an existing contract for testing.
    """
    # Get client with contracts
    client_data = client_queries.get_client_with_contracts(test_client_id)
    if not client_data or not client_data['contracts']:
        pytest.skip("No contracts found for test client")
    
    return client_data['contracts'][0]['contract_id']