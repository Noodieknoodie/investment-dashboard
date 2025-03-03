"""
Tests for database connection functionality.
"""
import pytest
import sqlite3
from database.connection import test_connection, get_db_connection
from database.connection import execute_query, execute_single_query, execute_insert

def test_connection_success():
    """
    Test that database connection is successful.
    """
    assert test_connection() is True, "Database connection test failed"

def test_get_db_connection():
    """
    Test that get_db_connection returns a valid connection.
    """
    conn = get_db_connection()
    assert isinstance(conn, sqlite3.Connection), "Connection object not returned"
    
    # Test that connection has row factory set
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test")
    row = cursor.fetchone()
    assert hasattr(row, 'keys'), "Row factory not set correctly"
    assert row['test'] == 1, "Row factory not returning proper values"
    
    conn.close()

def test_execute_query(db_connection):
    """
    Test that execute_query returns results.
    """
    # Simple query that should return results
    results = execute_query("SELECT * FROM clients LIMIT 5")
    assert isinstance(results, list), "Results should be a list"
    assert len(results) <= 5, "Query should return at most 5 results"

def test_execute_single_query(db_connection):
    """
    Test that execute_single_query returns a single result.
    """
    # Simple query that should return a single row
    result = execute_single_query("SELECT * FROM clients LIMIT 1")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'client_id' in result, "Result should have client_id key"

def test_execute_query_with_params(db_connection):
    """
    Test that execute_query works with parameters.
    """
    # Get client with ID 1
    results = execute_query("SELECT * FROM clients WHERE client_id = ?", (1,))
    if results:
        assert results[0]['client_id'] == 1, "Query with params not returning correct results"