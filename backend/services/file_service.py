# backend/services/file_service.py
# File system operations


from database.queries import files as file_queries
from database.queries import clients as client_queries
from typing import List, Dict, Any, Optional, BinaryIO
from pathlib import Path
import os
import shutil
from datetime import datetime
import mimetypes

# Supported file extensions
SUPPORTED_EXTENSIONS = [
    '.pdf', '.png', '.jpeg', '.jpg', '.tiff', '.webp',
    '.docx', '.doc', '.csv', '.xls', '.xlsx', '.txt'
]

def get_client_files(client_id: int) -> List[Dict[str, Any]]:
    """
    Get all files for a client.
    
    Args:
        client_id: Client ID
        
    Returns:
        List of file dictionaries
    """
    return file_queries.get_client_files(client_id)

def get_payment_files(payment_id: int) -> List[Dict[str, Any]]:
    """
    Get files linked to a payment.
    
    Args:
        payment_id: Payment ID
        
    Returns:
        List of file dictionaries
    """
    from database.queries import payments as payment_queries
    return payment_queries.get_payment_files(payment_id)

def get_onedrive_root_path() -> Path:
    """
    Get the root path to OneDrive documents folder.
    
    Returns:
        Path object for OneDrive root
    """
    # In a real implementation, this would detect the OneDrive folder location
    # For now, we'll use a placeholder path
    
    # Option 1: Default OneDrive location
    default_path = Path(os.path.expanduser("~/OneDrive"))
    if default_path.exists():
        return default_path
    
    # Option 2: OneDrive for Business
    business_path = Path(os.path.expanduser("~/OneDrive - Hohimer Wealth Management"))
    if business_path.exists():
        return business_path
    
    # For development/testing, return a temp directory
    return Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_onedrive"))

def get_client_folder_path(client_id: int) -> Path:
    """
    Get the OneDrive folder path for a client.
    
    Args:
        client_id: Client ID
        
    Returns:
        Path object for client folder
    """
    # Get client data
    client = client_queries.get_client_by_id(client_id)
    if not client or not client.get('onedrive_folder_path'):
        # If no folder path specified, use default based on client ID
        return get_onedrive_root_path() / f"client_{client_id}"
    
    # Use specified path
    folder_path = client['onedrive_folder_path']
    if not folder_path.startswith('/'):
        folder_path = '/' + folder_path
    
    # Normalize path
    onedrive_path = get_onedrive_root_path() / folder_path.lstrip('/')
    
    # Ensure folder exists
    os.makedirs(onedrive_path, exist_ok=True)
    
    return onedrive_path

def get_payment_folder_path(client_id: int) -> Path:
    """
    Get the payments subfolder path for a client.
    
    Args:
        client_id: Client ID
        
    Returns:
        Path object for payments folder
    """
    payment_path = get_client_folder_path(client_id) / "payments"
    
    # Ensure folder exists
    os.makedirs(payment_path, exist_ok=True)
    
    return payment_path

def is_valid_file_type(filename: str) -> bool:
    """
    Check if a file has a supported extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if file type is supported, False otherwise
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_EXTENSIONS

def save_file(client_id: int, file_obj: BinaryIO, filename: str, for_payment: bool = False) -> Dict[str, Any]:
    """
    Save a file to OneDrive and record in database.
    
    Args:
        client_id: Client ID
        file_obj: File object
        filename: Name of the file
        for_payment: Whether file is related to a payment
        
    Returns:
        Dictionary with file information
    """
    # Check file type
    if not is_valid_file_type(filename):
        valid_extensions = ", ".join(SUPPORTED_EXTENSIONS)
        raise ValueError(f"Unsupported file type. Supported types: {valid_extensions}")
    
    # Determine destination folder
    if for_payment:
        dest_folder = get_payment_folder_path(client_id)
    else:
        dest_folder = get_client_folder_path(client_id)
    
    # Create folder if it doesn't exist
    os.makedirs(dest_folder, exist_ok=True)
    
    # Handle filename conflicts by appending timestamp if needed
    base_name, extension = os.path.splitext(filename)
    dest_path = dest_folder / filename
    
    if os.path.exists(dest_path):
        # Append timestamp to make unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{base_name}_{timestamp}{extension}"
        dest_path = dest_folder / filename
    
    # Save file
    with open(dest_path, 'wb') as f:
        shutil.copyfileobj(file_obj, f)
    
    # Create relative path for storage
    onedrive_root = get_onedrive_root_path()
    relative_path = str(dest_path.relative_to(onedrive_root))
    
    # Record in database
    file_id = file_queries.create_file(client_id, filename, relative_path)
    
    return {
        "file_id": file_id,
        "client_id": client_id,
        "file_name": filename,
        "onedrive_path": relative_path
    }

def link_file_to_payment(payment_id: int, file_id: int) -> Dict[str, bool]:
    """
    Link an existing file to a payment.
    
    Args:
        payment_id: Payment ID
        file_id: File ID
        
    Returns:
        Dictionary with success status
    """
    success = file_queries.link_file_to_payment(payment_id, file_id)
    return {"success": success}

def unlink_file_from_payment(payment_id: int, file_id: int) -> Dict[str, bool]:
    """
    Unlink a file from a payment.
    
    Args:
        payment_id: Payment ID
        file_id: File ID
        
    Returns:
        Dictionary with success status
    """
    success = file_queries.unlink_file_from_payment(payment_id, file_id)
    return {"success": success}

def delete_file(file_id: int, delete_physical: bool = False) -> Dict[str, Any]:
    """
    Delete a file from the database and optionally from disk.
    
    Args:
        file_id: File ID
        delete_physical: Whether to delete the physical file
        
    Returns:
        Dictionary with deletion status
    """
    # Check if file is linked to payments
    payment_count = file_queries.get_payment_count_for_file(file_id)
    if payment_count > 0:
        return {
            "success": False,
            "message": f"File is linked to {payment_count} payments. Remove these links first."
        }
    
    # Get file info for deletion
    file_info = file_queries.get_file_by_id(file_id)
    if not file_info:
        return {"success": False, "message": "File not found"}
    
    # Delete physical file if requested
    if delete_physical:
        onedrive_path = get_onedrive_root_path() / file_info['onedrive_path']
        try:
            if os.path.exists(onedrive_path):
                os.remove(onedrive_path)
        except OSError as e:
            return {"success": False, "message": f"Error deleting file: {str(e)}"}
    
    # Delete from database
    success = file_queries.delete_file(file_id)
    if not success:
        return {"success": False, "message": "Error deleting file record"}
    
    return {"success": True}

def get_file_content(file_id: int) -> Dict[str, Any]:
    """
    Get file content and metadata for display.
    
    Args:
        file_id: File ID
        
    Returns:
        Dictionary with file content and metadata
    """
    # Get file info
    file_info = file_queries.get_file_by_id(file_id)
    if not file_info:
        return {"success": False, "message": "File not found"}
    
    # Get full path
    file_path = get_onedrive_root_path() / file_info['onedrive_path']
    
    # Check if file exists
    if not os.path.exists(file_path):
        return {"success": False, "message": "File not found on disk"}
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    # Read first part of file for preview (for text files)
    preview = None
    is_text = mime_type.startswith('text/') or mime_type in [
        'application/csv', 
        'application/json',
        'application/xml'
    ]
    
    if is_text and file_size < 1024 * 1024:  # Only preview if < 1MB
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                preview = f.read(4096)  # Read first 4KB
        except UnicodeDecodeError:
            # Not a text file after all
            preview = None
    
    return {
        "success": True,
        "file_id": file_info['file_id'],
        "client_id": file_info['client_id'],
        "file_name": file_info['file_name'],
        "onedrive_path": file_info['onedrive_path'],
        "uploaded_at": file_info['uploaded_at'],
        "file_size": file_size,
        "mime_type": mime_type,
        "preview": preview,
        "is_text": is_text,
        "file_path": str(file_path)
    }

def search_client_files(client_id: int, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for files by name for a client.
    
    Args:
        client_id: Client ID
        search_term: Search term
        
    Returns:
        List of matching file dictionaries
    """
    return file_queries.search_client_files(client_id, search_term)