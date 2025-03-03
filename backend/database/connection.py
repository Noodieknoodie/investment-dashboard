# backend/database/connection.py
# SQLite connection handling


import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, Generator, Any

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', '401KDB.db')

def get_db_connection() -> sqlite3.Connection:
    """
    Creates and returns a new SQLite database connection.
    Connection has row factory set to return results as dictionaries.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys support
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        # Log the error (would be better with a proper logging setup)
        print(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager for database operations.
    Provides a cursor and handles connection/transaction management.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[tuple] = None) -> list:
    """
    Execute a SELECT query and return all results.
    
    Args:
        query: SQL query string
        params: Query parameters as tuple
        
    Returns:
        List of rows as dictionaries
    """
    with get_db_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def execute_single_query(query: str, params: Optional[tuple] = None) -> Optional[dict]:
    """
    Execute a SELECT query and return a single result or None.
    
    Args:
        query: SQL query string
        params: Query parameters as tuple
        
    Returns:
        Single row as dictionary or None if no result
    """
    with get_db_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        return dict(row) if row else None

def execute_insert(query: str, params: tuple) -> int:
    """
    Execute an INSERT query and return the ID of the inserted row.
    
    Args:
        query: SQL query string
        params: Query parameters as tuple
        
    Returns:
        ID of the last inserted row
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.lastrowid

def execute_update(query: str, params: tuple) -> int:
    """
    Execute an UPDATE query and return the number of affected rows.
    
    Args:
        query: SQL query string
        params: Query parameters as tuple
        
    Returns:
        Number of affected rows
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount

def execute_delete(query: str, params: tuple) -> int:
    """
    Execute a DELETE query and return the number of affected rows.
    
    Args:
        query: SQL query string
        params: Query parameters as tuple
        
    Returns:
        Number of affected rows
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.rowcount

def test_connection() -> bool:
    """
    Test database connection and return success status.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False