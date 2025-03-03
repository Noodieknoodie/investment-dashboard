# backend/routers/payments.py
# Payment endpoints


from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional, Dict, Any
from services import payment_service
from models.schemas import PaymentCreate, PaymentUpdate, PaymentWithDetails, ExpectedFeeRequest, ExpectedFeeResponse, PaginatedResponse

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}}
)

@router.get("/{client_id}")
async def get_client_payments(
    client_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Get paginated payment history for a client"""
    try:
        return payment_service.get_client_payments(client_id, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detail/{payment_id}", response_model=PaymentWithDetails)
async def get_payment_details(payment_id: int):
    """Get detailed information for a specific payment"""
    payment = payment_service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/")
async def create_payment(payment: PaymentCreate):
    """Create a new payment or split payment"""
    try:
        result = payment_service.create_payment(payment)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{payment_id}")
async def update_payment(payment_id: int, payment: PaymentUpdate):
    """Update an existing payment"""
    try:
        result = payment_service.update_payment(payment_id, payment)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{payment_id}")
async def delete_payment(payment_id: int):
    """Delete a payment"""
    try:
        result = payment_service.delete_payment(payment_id)
        if not result["success"]:
            if result.get("requires_confirmation"):
                # Return information about split payment group
                return result
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/split-group/{split_group_id}")
async def delete_split_payment_group(split_group_id: str):
    """Delete all payments in a split payment group"""
    try:
        result = payment_service.delete_split_payment_group(split_group_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expected-fee", response_model=ExpectedFeeResponse)
async def calculate_expected_fee(request: ExpectedFeeRequest):
    """Calculate expected fee based on contract and assets"""
    try:
        return payment_service.calculate_expected_fee(
            client_id=request.client_id,
            contract_id=request.contract_id,
            total_assets=request.total_assets,
            period_type=request.period_type,
            period=request.period,
            year=request.year
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-periods/{client_id}/{contract_id}")
async def get_available_periods(client_id: int, contract_id: int):
    """Get available periods for payment entry based on contract"""
    try:
        return payment_service.get_available_periods(client_id, contract_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


        