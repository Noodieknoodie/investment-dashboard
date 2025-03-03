# backend/routers/clients.py
# Client endpoints

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from services import client_service
from models.schemas import Client, ClientSnapshot

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