# backend/database/queries/files.py
# Document/file-related queries

from database.connection import execute_query, execute_single_query, execute_insert, execute_update, execute_delete
from typing import List, Dict, Any, Optional

def get_client_files(client_id: int) -> List[Dict[str, Any]]:

    query = """
    SELECT 
        file_id,
        client_id,
        file_name,
        onedrive_path,
        uploaded_at
    FROM 
        client_files
    WHERE 
        client_id = ?
    ORDER BY 
        uploaded_at DESC
    """
    
    return execute_query(query, (client_id,))

def get_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:

    query = """
    SELECT 
        file_id,
        client_id,
        file_name,
        onedrive_path,
        uploaded_at
    FROM 
        client_files
    WHERE 
        file_id = ?
    """
    
    return execute_single_query(query, (file_id,))

def create_file(client_id: int, file_name: str, onedrive_path: str) -> int:

    query = """
    INSERT INTO client_files (
        client_id,
        file_name,
        onedrive_path
    ) VALUES (?, ?, ?)
    """
    
    return execute_insert(query, (client_id, file_name, onedrive_path))

def delete_file(file_id: int) -> bool:

    query = """
    DELETE FROM client_files
    WHERE file_id = ?
    """
    
    rows_deleted = execute_delete(query, (file_id,))
    return rows_deleted > 0

def link_file_to_payment(payment_id: int, file_id: int) -> bool:

    query = """
    INSERT OR IGNORE INTO payment_files (
        payment_id,
        file_id
    ) VALUES (?, ?)
    """
    
    try:
        execute_insert(query, (payment_id, file_id))
        return True
    except Exception:
        return False

def unlink_file_from_payment(payment_id: int, file_id: int) -> bool:

    query = """
    DELETE FROM payment_files
    WHERE payment_id = ? AND file_id = ?
    """
    
    rows_deleted = execute_delete(query, (payment_id, file_id))
    return rows_deleted > 0

def get_payment_count_for_file(file_id: int) -> int:

    query = """
    SELECT COUNT(*) as count
    FROM payment_files
    WHERE file_id = ?
    """
    
    result = execute_single_query(query, (file_id,))
    return result['count'] if result else 0

def get_file_exists(client_id: int, file_name: str) -> bool:

    query = """
    SELECT COUNT(*) as count
    FROM client_files
    WHERE client_id = ? AND file_name = ?
    """
    
    result = execute_single_query(query, (client_id, file_name))
    return result['count'] > 0 if result else False

def find_file_by_path(client_id: int, onedrive_path: str) -> Optional[Dict[str, Any]]:

    # Normalize path (replace backslashes with forward slashes)
    normalized_path = onedrive_path.replace('\\', '/')
    
    query = """
    SELECT 
        file_id,
        client_id,
        file_name,
        onedrive_path,
        uploaded_at
    FROM 
        client_files
    WHERE 
        client_id = ? AND
        onedrive_path = ?
    """
    
    return execute_single_query(query, (client_id, normalized_path))

def search_client_files(client_id: int, search_term: str) -> List[Dict[str, Any]]:

    query = """
    SELECT 
        file_id,
        client_id,
        file_name,
        onedrive_path,
        uploaded_at
    FROM 
        client_files
    WHERE 
        client_id = ? AND
        (file_name LIKE ? OR onedrive_path LIKE ?)
    ORDER BY 
        uploaded_at DESC
    """
    
    search_pattern = f"%{search_term}%"
    return execute_query(query, (client_id, search_pattern, search_pattern))