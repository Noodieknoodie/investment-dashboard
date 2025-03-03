# backend/routers/files.py
# File handling endpoints

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from services import file_service
import os

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}}
)

@router.get("/{client_id}")
async def get_client_files(client_id: int):
    """Get all files for a client"""
    try:
        return file_service.get_client_files(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment/{payment_id}")
async def get_payment_files(payment_id: int):
    """Get files linked to a payment"""
    try:
        return file_service.get_payment_files(payment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/{client_id}")
async def upload_file(
    client_id: int,
    file: UploadFile = File(...),
    for_payment: bool = Form(False)
):
    """Upload a file for a client"""
    try:
        # Check if file is empty
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Save the file
        result = file_service.save_file(
            client_id=client_id,
            file_obj=file.file,
            filename=file.filename,
            for_payment=for_payment
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/link/{payment_id}/{file_id}")
async def link_file_to_payment(payment_id: int, file_id: int):
    """Link a file to a payment"""
    try:
        result = file_service.link_file_to_payment(payment_id, file_id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to link file")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/link/{payment_id}/{file_id}")
async def unlink_file_from_payment(payment_id: int, file_id: int):
    """Unlink a file from a payment"""
    try:
        result = file_service.unlink_file_from_payment(payment_id, file_id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to unlink file")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(file_id: int, delete_physical: bool = Query(False)):
    """Delete a file"""
    try:
        result = file_service.delete_file(file_id, delete_physical)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{file_id}")
async def get_file_content(file_id: int):
    """Get file content and metadata"""
    try:
        result = file_service.get_file_content(file_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_id}")
async def download_file(file_id: int):
    """Download a file"""
    try:
        # Get file information
        file_info = file_service.get_file_content(file_id)
        if not file_info["success"]:
            raise HTTPException(status_code=404, detail=file_info["message"])
        
        # Return file as download
        return FileResponse(
            path=file_info["file_path"],
            filename=file_info["file_name"],
            media_type=file_info["mime_type"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{client_id}")
async def search_client_files(client_id: int, search: str = Query(...)):
    """Search for client files by name"""
    try:
        return file_service.search_client_files(client_id, search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))