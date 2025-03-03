# backend/database/queries/files.py
# Document/file-related queries

from database.connection import execute_query, execute_single_query, execute_insert, execute_update, execute_delete
from typing import List, Dict, Any, Optional

def get_client_files(client_id: int) -> List[Dict[str, Any]]:
    """
    Get all files for a client.
    
    Args:
        client_id: Client ID
        
    Returns:
        List of file dictionaries
    """
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
    """
    Get a single file by ID.
    
    Args:
        file_id: File ID
        
    Returns:
        File dictionary or None if not found
    """
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
    """
    Create a new file record.
    
    Args:
        client_id: Client ID
        file_name: Name of the file
        onedrive_path: Path to the file in OneDrive
        
    Returns:
        ID of the newly created file
    """
    query = """
    INSERT INTO client_files (
        client_id,
        file_name,
        onedrive_path
    ) VALUES (?, ?, ?)
    """
    
    return execute_insert(query, (client_id, file_name, onedrive_path))

def delete_file(file_id: int) -> bool:
    """
    Delete a file record.
    Note: This does not delete the actual file from OneDrive.
    
    Args:
        file_id: File ID to delete
        
    Returns:
        True if deletion successful, False otherwise
    """
    query = """
    DELETE FROM client_files
    WHERE file_id = ?
    """
    
    rows_deleted = execute_delete(query, (file_id,))
    return rows_deleted > 0

def link_file_to_payment(payment_id: int, file_id: int) -> bool:
    """
    Link a file to a payment.
    
    Args:
        payment_id: Payment ID
        file_id: File ID
        
    Returns:
        True if linking successful, False otherwise
    """
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
    """
    Unlink a file from a payment.
    
    Args:
        payment_id: Payment ID
        file_id: File ID
        
    Returns:
        True if unlinking successful, False otherwise
    """
    query = """
    DELETE FROM payment_files
    WHERE payment_id = ? AND file_id = ?
    """
    
    rows_deleted = execute_delete(query, (payment_id, file_id))
    return rows_deleted > 0

def get_payment_count_for_file(file_id: int) -> int:
    """
    Get the number of payments a file is linked to.
    
    Args:
        file_id: File ID
        
    Returns:
        Number of linked payments
    """
    query = """
    SELECT COUNT(*) as count
    FROM payment_files
    WHERE file_id = ?
    """
    
    result = execute_single_query(query, (file_id,))
    return result['count'] if result else 0

def get_file_exists(client_id: int, file_name: str) -> bool:
    """
    Check if a file already exists for a client.
    
    Args:
        client_id: Client ID
        file_name: Name of the file
        
    Returns:
        True if file exists, False otherwise
    """
    query = """
    SELECT COUNT(*) as count
    FROM client_files
    WHERE client_id = ? AND file_name = ?
    """
    
    result = execute_single_query(query, (client_id, file_name))
    return result['count'] > 0 if result else False

def search_client_files(client_id: int, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for files by name for a client.
    
    Args:
        client_id: Client ID
        search_term: Search term for file name
        
    Returns:
        List of matching file dictionaries
    """
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
        file_name LIKE ?
    ORDER BY 
        uploaded_at DESC
    """
    
    return execute_query(query, (client_id, f"%{search_term}%"))