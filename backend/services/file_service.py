# backend/services/file_service.py
# File system operations for handling documents in shared OneDrive

from database.queries import files as file_queries
from database.queries import clients as client_queries
from typing import List, Dict, Any, Optional, BinaryIO, Tuple
from pathlib import Path
import os
import sys
import json
import shutil
from datetime import datetime
import mimetypes

# Supported file extensions
SUPPORTED_EXTENSIONS = [
    '.pdf', '.png', '.jpeg', '.jpg', '.tiff', '.webp',
    '.docx', '.doc', '.csv', '.xls', '.xlsx', '.txt'
]

# Config file path for shared folder settings
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "file_paths.json")

def get_client_files(client_id: int) -> List[Dict[str, Any]]:
    """
    Get all files for a client from the database.
    
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

def get_shared_folder_path() -> Tuple[Path, str]:
    """
    Get the path to the shared team folder where documents are stored.
    Adapts to different user environments.
    
    Returns:
        Tuple of (full path to shared folder, base path used)
    """
    # Default path components
    default_shared_path = "Hohimer Wealth Management\\Hohimer Company Portal - Company\\Hohimer Team Shared 4-15-19"
    
    # Try to load from config if it exists
    config_path = default_shared_path
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'shared_folder_path' in config:
                    config_path = config['shared_folder_path']
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Determine user home directory
    user_home = os.path.expanduser("~")
    
    # List of possible path patterns to try
    possible_paths = [
        # Standard Windows OneDrive path
        os.path.join(user_home, config_path),
        # Alternate path structure
        os.path.join(user_home, "OneDrive - Hohimer Wealth Management", config_path.split("Hohimer Wealth Management\\")[1]) 
        if "\\" in config_path else "",
        # Possible Linux path
        os.path.join(user_home, config_path.replace("\\", "/")),
    ]
    
    # Try each path
    for path in possible_paths:
        if path and os.path.exists(path):
            return Path(path), config_path
    
    # If no paths work, create a temp directory for development
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_onedrive")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"WARNING: Could not find shared folder. Using temp dir: {temp_dir}")
    return Path(temp_dir), "temp_onedrive"

def save_shared_folder_config(path: str) -> bool:
    """
    Save the shared folder path to config.
    
    Args:
        path: Path to save
        
    Returns:
        Success status
    """
    try:
        # Ensure config directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # Load existing config or create new
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        
        # Update shared folder path
        config['shared_folder_path'] = path
        
        # Save config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_client_folder_path(client_id: int) -> Path:
    """
    Get the path to a client's folder in the shared directory.
    Uses the client's onedrive_folder_path from the database.
    
    Args:
        client_id: Client ID
        
    Returns:
        Path object for client folder
    """
    # Get the shared folder base path
    shared_folder, _ = get_shared_folder_path()
    
    # Get client data
    client = client_queries.get_client_by_id(client_id)
    if not client or not client.get('onedrive_folder_path'):
        # If no folder path specified, use "Unknown Client" folder
        client_path = Path(shared_folder) / "Unknown Clients" / f"Client_{client_id}"
        # Ensure folder exists
        os.makedirs(client_path, exist_ok=True)
        return client_path
    
    # Use specified path (normalize slashes)
    folder_path = client['onedrive_folder_path'].replace('/', '\\')
    
    # Check if path is already absolute
    if os.path.isabs(folder_path):
        return Path(folder_path)
    
    # Combine with shared folder path
    client_path = Path(shared_folder) / folder_path
    
    # Check if directory exists
    if not os.path.exists(client_path):
        print(f"WARNING: Client folder not found: {client_path}")
    
    return client_path

def scan_client_directory(client_id: int, register_files: bool = False) -> Dict[str, Any]:
    """
    Scan a client's directory and optionally register files in the database.
    
    Args:
        client_id: Client ID
        register_files: Whether to register found files in the database
        
    Returns:
        Dictionary with directory structure
    """
    client_path = get_client_folder_path(client_id)
    shared_folder, base_path = get_shared_folder_path()
    
    # Check if path exists
    if not os.path.exists(client_path):
        return {
            "success": False,
            "message": f"Client directory not found: {client_path}",
            "files": [],
            "directories": []
        }
    
    # Get existing files from database
    db_files = file_queries.get_client_files(client_id)
    existing_files = {f['onedrive_path']: f for f in db_files}
    
    # Track files and directories
    files = []
    directories = []
    new_files_count = 0
    
    # Walk directory
    for root, dirs, filenames in os.walk(client_path):
        # Get relative path from shared folder
        try:
            rel_root = os.path.relpath(root, shared_folder)
        except ValueError:
            # If not relative to shared folder, use absolute path
            rel_root = root
            
        if rel_root == '.':
            rel_root = ''
            
        # Add directories
        for dir_name in dirs:
            dir_path = os.path.join(rel_root, dir_name)
            directories.append({
                "name": dir_name,
                "path": dir_path.replace('\\', '/'),
                "full_path": os.path.join(root, dir_name)
            })
        
        # Add files
        for file_name in filenames:
            file_path = os.path.join(rel_root, file_name)
            file_path_norm = file_path.replace('\\', '/')
            full_path = os.path.join(root, file_name)
            
            # Only include supported file types
            if not is_valid_file_type(file_name):
                continue
                
            # Check if file already registered
            if file_path_norm in existing_files:
                # File already registered
                file_info = existing_files[file_path_norm]
                files.append({
                    "file_id": file_info['file_id'],
                    "name": file_name,
                    "path": file_path_norm,
                    "full_path": full_path,
                    "size": os.path.getsize(full_path),
                    "registered": True,
                    "uploaded_at": file_info['uploaded_at']
                })
            else:
                # New file
                file_info = {
                    "file_id": None,
                    "name": file_name,
                    "path": file_path_norm,
                    "full_path": full_path,
                    "size": os.path.getsize(full_path),
                    "registered": False,
                    "uploaded_at": None
                }
                
                # Register file if requested
                if register_files:
                    try:
                        file_id = file_queries.create_file(client_id, file_name, file_path_norm)
                        file_info["file_id"] = file_id
                        file_info["registered"] = True
                        file_info["uploaded_at"] = datetime.now().isoformat()
                        new_files_count += 1
                    except Exception as e:
                        print(f"Error registering file {file_path_norm}: {e}")
                
                files.append(file_info)
    
    return {
        "success": True,
        "client_id": client_id,
        "base_path": str(client_path),
        "files": files,
        "directories": directories,
        "new_files_registered": new_files_count
    }

def get_consulting_fee_folder(client_id: int, year: Optional[int] = None) -> Path:
    """
    Get the path to a client's consulting fee folder for a specific year.
    Creates the folder if it doesn't exist.
    
    Args:
        client_id: Client ID
        year: Year (defaults to current year)
        
    Returns:
        Path to consulting fee folder
    """
    if year is None:
        year = datetime.now().year
        
    client_path = get_client_folder_path(client_id)
    fee_path = client_path / "Consulting Fee" / str(year)
    
    # Create directory if it doesn't exist
    os.makedirs(fee_path, exist_ok=True)
    
    return fee_path

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

def register_existing_file(client_id: int, file_path: str) -> Dict[str, Any]:
    """
    Register an existing file in the database.
    
    Args:
        client_id: Client ID
        file_path: Path to the file (absolute or relative to shared folder)
        
    Returns:
        Dictionary with file information
    """
    shared_folder, _ = get_shared_folder_path()
    
    # Check if path is absolute or relative
    if os.path.isabs(file_path):
        # Convert to relative path
        try:
            rel_path = os.path.relpath(file_path, shared_folder)
        except ValueError:
            return {"success": False, "message": "File is not in shared folder"}
    else:
        # Already relative
        rel_path = file_path.replace('\\', '/')
    
    # Get filename
    filename = os.path.basename(file_path)
    
    # Check if file exists
    full_path = os.path.join(shared_folder, rel_path)
    if not os.path.exists(full_path):
        return {"success": False, "message": f"File not found: {full_path}"}
    
    # Check if already registered
    existing_files = file_queries.get_client_files(client_id)
    for file in existing_files:
        if file['onedrive_path'].replace('\\', '/') == rel_path.replace('\\', '/'):
            return {
                "success": True,
                "message": "File already registered",
                "file_id": file['file_id'],
                "client_id": client_id,
                "file_name": filename,
                "onedrive_path": rel_path
            }
    
    # Register file
    file_id = file_queries.create_file(client_id, filename, rel_path)
    
    return {
        "success": True,
        "file_id": file_id,
        "client_id": client_id,
        "file_name": filename,
        "onedrive_path": rel_path
    }

def save_file(client_id: int, file_obj: BinaryIO, filename: str, for_payment: bool = False, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Save a file to the client's folder and record in database.
    
    Args:
        client_id: Client ID
        file_obj: File object
        filename: Name of the file
        for_payment: Whether file is related to a payment
        year: Year folder to use (for payment files)
        
    Returns:
        Dictionary with file information
    """
    # Check file type
    if not is_valid_file_type(filename):
        valid_extensions = ", ".join(SUPPORTED_EXTENSIONS)
        raise ValueError(f"Unsupported file type. Supported types: {valid_extensions}")
    
    # Determine destination folder
    if for_payment:
        # Use Consulting Fee/{year} folder
        dest_folder = get_consulting_fee_folder(client_id, year)
    else:
        # Use main client folder
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
    
    # Get shared folder for relative path calculation
    shared_folder, _ = get_shared_folder_path()
    
    # Create relative path for storage
    try:
        relative_path = str(dest_path.relative_to(shared_folder))
    except ValueError:
        # If not relative to shared folder, store absolute path
        relative_path = str(dest_path)
    
    # Record in database
    file_id = file_queries.create_file(client_id, filename, relative_path)
    
    return {
        "success": True,
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
        shared_folder, _ = get_shared_folder_path()
        file_path = shared_folder / file_info['onedrive_path']
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
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
    shared_folder, _ = get_shared_folder_path()
    file_path = shared_folder / file_info['onedrive_path']
    
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
    
    # TODO: Add preview support for PDF and other document types
    # This would require additional libraries like pdf2image, python-docx, etc.
    
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