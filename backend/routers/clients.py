# backend/routers/clients.py
# Client endpoints

from fastapi import APIRouter, HTTPException, Query, Form
from typing import List, Optional, Dict, Any
from services import client_service
from models.schemas import Client, ClientSnapshot, Contract
from database.queries import get_client_by_id, get_client_contracts

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Client])
async def get_all_clients():
    """Get a list of all clients"""
    return client_service.get_all_clients()

@router.get("/by-provider")
async def get_clients_by_provider():
    """Get clients grouped by provider"""
    return client_service.get_clients_by_provider()

@router.get("/{client_id}", response_model=ClientSnapshot)
async def get_client_details(client_id: int):
    """Get detailed information for a specific client"""
    client = client_service.get_client_snapshot(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{client_id}/compliance-status")
async def get_client_compliance_status(client_id: int):
    """Get compliance status for a client"""
    try:
        return client_service.get_client_compliance_status(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{client_id}/fee-summary")
async def get_client_fee_summary(client_id: int):
    """Get fee summary information for a client"""
    try:
        return client_service.calculate_fee_summary(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@router.put("/{client_id}/folder-path")
async def update_client_folder_path(client_id: int, folder_path: str = Form(...)):
    """Update a client's OneDrive folder path"""
    try:
        result = client_service.update_client_folder_path(client_id, folder_path)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{client_id}/contracts", response_model=List[Contract])
async def get_contracts_for_client(client_id: int):
    """
    Get all valid contracts for a specific client.
    
    This helps the frontend select only valid contract-client combinations.
    """
    # First check if client exists
    client = get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client not found with id {client_id}")
    
    # Get contracts for the client
    contracts = get_client_contracts(client_id)
    
    # Return contracts (empty list is fine)
    return contracts