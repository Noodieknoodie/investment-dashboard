# backend/services/payment_service.py
# Payment calculation, validation

from database.queries import payments as payment_queries
from database.queries import clients as client_queries
from models.schemas import Payment, PaymentCreate, PaymentUpdate, PaymentWithDetails, PaginatedResponse
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import uuid
import re
from fastapi import HTTPException

def get_client_payments(client_id: int, page: int = 1, page_size: int = 20) -> PaginatedResponse:
    """
    Get paginated payments for a client.
    
    Args:
        client_id: Client ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        PaginatedResponse with payment items
    """
    # Check if client exists
    client = client_queries.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get payments with total count
    payments, total = payment_queries.get_client_payments(client_id, page_size, offset)
    
    # Return paginated response
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=payments
    )

def get_payment_by_id(payment_id: int) -> Optional[PaymentWithDetails]:
    """
    Get payment with detailed information.
    
    Args:
        payment_id: Payment ID
        
    Returns:
        PaymentWithDetails object or None if not found
    """
    payment = payment_queries.get_payment_by_id(payment_id)
    if not payment:
        return None
    
    # Get associated files
    files = payment_queries.get_payment_files(payment_id)
    
    # Create PaymentWithDetails object
    payment_detail = PaymentWithDetails(**payment, files=files)
    return payment_detail

def create_payment(payment_data: PaymentCreate) -> Dict[str, Any]:
    """
    Create a new payment or split payment.
    
    Args:
        payment_data: Payment data
        
    Returns:
        Dictionary with created payment(s) info
    """
    # Get contract for payment schedule
    client_data = client_queries.get_client_with_contracts(payment_data.client_id)
    if not client_data or not client_data['contracts']:
        raise ValueError("Client or contract not found")
    
    # Find contract matching contract_id
    contract = next((c for c in client_data['contracts'] if c['contract_id'] == payment_data.contract_id), None)
    if not contract:
        raise ValueError(f"Contract {payment_data.contract_id} not found for client {payment_data.client_id}")
    
    # Determine if monthly or quarterly schedule
    is_monthly = contract['payment_schedule'].lower() == 'monthly'
    period_type = 'month' if is_monthly else 'quarter'
    
    # Calculate expected fee if assets provided
    expected_fee = None
    if payment_data.total_assets is not None:
        expected_fee = payment_queries.calculate_expected_fee(
            payment_data.contract_id, 
            payment_data.total_assets, 
            period_type
        )
    
    # Handle split payments
    if payment_data.is_split_payment:
        # Validate end period is provided
        if payment_data.end_period is None or payment_data.end_period_year is None:
            raise ValueError("End period is required for split payments")
        
        # Validate end period is not before start period
        start_total = payment_data.start_period_year * (12 if is_monthly else 4) + payment_data.start_period
        end_total = payment_data.end_period_year * (12 if is_monthly else 4) + payment_data.end_period
        
        if end_total < start_total:
            raise ValueError("End period cannot be before start period")
        
        # Create split payments
        payment_ids = payment_queries.create_split_payments(
            contract_id=payment_data.contract_id,
            client_id=payment_data.client_id,
            received_date=payment_data.received_date,
            total_assets=payment_data.total_assets,
            expected_fee=expected_fee,
            actual_fee=float(payment_data.actual_fee),
            method=payment_data.method,
            notes=payment_data.notes,
            is_monthly=is_monthly,
            start_period=payment_data.start_period,
            start_period_year=payment_data.start_period_year,
            end_period=payment_data.end_period,
            end_period_year=payment_data.end_period_year
        )
        
        return {
            "success": True,
            "payment_ids": payment_ids,
            "is_split": True,
            "split_count": len(payment_ids),
            "split_group_id": payment_queries.get_payment_by_id(payment_ids[0]).get('split_group_id') if payment_ids else None
        }
    else:
        # Create a single payment
        # Map period fields based on schedule type
        if is_monthly:
            # Monthly payment
            payment_id = payment_queries.create_payment(
                contract_id=payment_data.contract_id,
                client_id=payment_data.client_id,
                received_date=payment_data.received_date,
                total_assets=payment_data.total_assets,
                expected_fee=expected_fee,
                actual_fee=float(payment_data.actual_fee),
                method=payment_data.method,
                notes=payment_data.notes,
                applied_start_month=payment_data.start_period,
                applied_start_month_year=payment_data.start_period_year,
                applied_end_month=payment_data.start_period,
                applied_end_month_year=payment_data.start_period_year,
                applied_start_quarter=None,
                applied_start_quarter_year=None,
                applied_end_quarter=None,
                applied_end_quarter_year=None
            )
        else:
            # Quarterly payment
            payment_id = payment_queries.create_payment(
                contract_id=payment_data.contract_id,
                client_id=payment_data.client_id,
                received_date=payment_data.received_date,
                total_assets=payment_data.total_assets,
                expected_fee=expected_fee,
                actual_fee=float(payment_data.actual_fee),
                method=payment_data.method,
                notes=payment_data.notes,
                applied_start_month=None,
                applied_start_month_year=None,
                applied_end_month=None,
                applied_end_month_year=None,
                applied_start_quarter=payment_data.start_period,
                applied_start_quarter_year=payment_data.start_period_year,
                applied_end_quarter=payment_data.start_period,
                applied_end_quarter_year=payment_data.start_period_year
            )
        
        return {
            "success": True,
            "payment_id": payment_id,
            "is_split": False
        }

def update_payment(payment_id: int, payment_data: PaymentUpdate) -> Dict[str, Any]:
    """
    Update an existing payment.
    
    Args:
        payment_id: Payment ID to update
        payment_data: Updated payment data
        
    Returns:
        Dictionary with update status
    """
    # First check if payment exists
    existing_payment = payment_queries.get_payment_by_id(payment_id)
    if not existing_payment:
        return {"success": False, "message": "Payment not found"}
    
    # Check if this is part of a split payment group
    if existing_payment.get('split_group_id'):
        return {
            "success": False, 
            "requires_confirmation": True,
            "message": "This payment is part of a split payment group. Editing one payment will affect the whole group.",
            "split_group_id": existing_payment['split_group_id']
        }
    
    # Convert Decimal to float for database
    actual_fee = float(payment_data.actual_fee) if payment_data.actual_fee is not None else None
    
    # Update payment
    success = payment_queries.update_payment(
        payment_id=payment_id,
        received_date=payment_data.received_date,
        total_assets=payment_data.total_assets,
        actual_fee=actual_fee,
        method=payment_data.method,
        notes=payment_data.notes
    )
    
    if not success:
        return {"success": False, "message": "Payment not found or no changes made"}
    
    # Recalculate expected fee if assets changed
    if payment_data.total_assets is not None:
        # Get contract and payment details
        payment = payment_queries.get_payment_by_id(payment_id)
        if payment:
            # Determine period type
            is_monthly = payment.get('applied_start_month') is not None
            period_type = 'month' if is_monthly else 'quarter'
            
            # Calculate new expected fee
            expected_fee = payment_queries.calculate_expected_fee(
                payment['contract_id'], 
                payment_data.total_assets, 
                period_type
            )
            
            # Update expected fee
            if expected_fee is not None:
                payment_queries.update_expected_fee(payment_id, expected_fee)
    
    return {"success": True, "payment_id": payment_id}

def delete_payment(payment_id: int) -> Dict[str, Any]:
    """
    Delete a payment.
    
    Args:
        payment_id: Payment ID to delete
        
    Returns:
        Dictionary with deletion status
    """
    # First check if this is part of a split payment group
    payment = payment_queries.get_payment_by_id(payment_id)
    if not payment:
        return {"success": False, "message": "Payment not found"}
    
    # If part of split payment group, ask if user wants to delete all related payments
    if payment.get('split_group_id'):
        split_payments = payment_queries.get_split_payment_group(payment['split_group_id'])
        return {
            "success": False,
            "requires_confirmation": True,
            "message": f"This payment is part of a split payment group with {len(split_payments)} payments. Do you want to delete all related payments?",
            "split_group_id": payment['split_group_id'],
            "split_count": len(split_payments)
        }
    
    # Delete single payment
    success = payment_queries.delete_payment(payment_id)
    if not success:
        return {"success": False, "message": "Failed to delete payment"}
    
    return {"success": True}

def delete_split_payment_group(split_group_id: str) -> Dict[str, Any]:
    """
    Delete all payments in a split payment group.
    
    Args:
        split_group_id: Split group ID
        
    Returns:
        Dictionary with deletion status
    """
    # Get all payments in the group
    payments = payment_queries.get_split_payment_group(split_group_id)
    if not payments:
        return {"success": False, "message": "No payments found in group"}
    
    # Delete each payment
    deleted_count = 0
    for payment in payments:
        if payment_queries.delete_payment(payment['payment_id']):
            deleted_count += 1
    
    if deleted_count == 0:
        return {"success": False, "message": "Failed to delete payments"}
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "total_count": len(payments)
    }

def calculate_expected_fee(
    client_id: int,
    contract_id: int,
    total_assets: Optional[int],
    period_type: str,
    period: int,
    year: int
) -> Dict[str, Any]:
    """
    Calculate expected fee for payment validation.
    
    Args:
        client_id: Client ID
        contract_id: Contract ID
        total_assets: Total assets (optional)
        period_type: 'month' or 'quarter'
        period: Period number (1-12 for months, 1-4 for quarters)
        year: Year
        
    Returns:
        Dictionary with expected fee and calculation details
    """
    # Validate period type
    if period_type not in ('month', 'quarter'):
        raise ValueError("Period type must be 'month' or 'quarter'")
    
    # Validate period number
    if period_type == 'month' and (period < 1 or period > 12):
        raise ValueError("Month must be between 1 and 12")
    if period_type == 'quarter' and (period < 1 or period > 4):
        raise ValueError("Quarter must be between 1 and 4")
    
    # Get client and contract
    client_data = client_queries.get_client_with_contracts(client_id)
    if not client_data or not client_data['contracts']:
        raise ValueError("Client or contract not found")
    
    # Find contract matching contract_id
    contract = next((c for c in client_data['contracts'] if c['contract_id'] == contract_id), None)
    if not contract:
        raise ValueError(f"Contract {contract_id} not found for client {client_id}")
    
    # Get fee type
    fee_type = contract['fee_type'].lower() if contract['fee_type'] else None
    
    # If total_assets not provided but fee type is percentage, try to get latest AUM
    if total_assets is None and fee_type in ('percentage', 'percent'):
        metrics = client_queries.get_client_metrics(client_id)
        if metrics and metrics.get('last_recorded_assets'):
            total_assets = int(metrics['last_recorded_assets'])
    
    # Calculate expected fee
    expected_fee = payment_queries.calculate_expected_fee(contract_id, total_assets, period_type)
    
    # Determine calculation method
    if fee_type == 'flat':
        flat_rate = contract['flat_rate']
        period_label = "monthly" if period_type == "month" else "quarterly"
        calculation_method = f"Flat fee ({period_label}): ${flat_rate:,.2f}"
    elif fee_type in ('percentage', 'percent'):
        if total_assets is not None:
            rate = contract['percent_rate']
            rate_percentage = float(rate) * 100
            calculation_method = f"{rate_percentage:.3f}% of ${total_assets:,}"
        else:
            calculation_method = "Percentage fee (assets not provided)"
    else:
        calculation_method = "Unknown fee type"
    
    return {
        "expected_fee": expected_fee,
        "fee_type": fee_type,
        "calculation_method": calculation_method
    }

def get_available_periods(client_id: int, contract_id: int) -> Dict[str, Any]:
    """
    Get available periods for payment entry based on contract start date.
    
    Args:
        client_id: Client ID
        contract_id: Contract ID
        
    Returns:
        Dictionary with available periods
    """
    # Check if client exists
    client = client_queries.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    
    # Check if contract exists and belongs to this client
    contract_query = """
        SELECT 
            contract_id, client_id, contract_number, provider_name,
            contract_start_date, fee_type, percent_rate, flat_rate,
            payment_schedule, num_people, notes
        FROM contracts
        WHERE contract_id = ? AND client_id = ? AND valid_to IS NULL
    """
    from database.connection import execute_single_query
    contract = execute_single_query(contract_query, (contract_id, client_id))
    
    if not contract:
        raise HTTPException(status_code=400, detail=f"Contract {contract_id} not found for client {client_id}")
    
    # Determine if monthly or quarterly
    is_monthly = contract['payment_schedule'].lower() == 'monthly'
    
    # Get contract start date
    contract_start = contract['contract_start_date']
    if not contract_start:
        # If no start date, use a default (beginning of current year)
        contract_start = f"{datetime.now().year}-01-01"
    
    try:
        # Try to parse the date
        start_date = datetime.strptime(contract_start, "%Y-%m-%d")
    except ValueError:
        # If date format is invalid, try another common format
        try:
            start_date = datetime.strptime(contract_start, "%Y-%m-%d")
        except ValueError:
            # If still invalid, use default
            start_date = datetime(datetime.now().year, 1, 1)
    
    # Calculate available periods based on contract start and current date
    current_date = datetime.now()
    periods = []
    
    if is_monthly:
        # For monthly payments, generate from contract start to current month - 1
        # Calculate starting month
        start_year = start_date.year
        start_month = start_date.month
        
        # Calculate current month (with 1 month behind for arrears)
        current_year = current_date.year
        current_month = current_date.month - 1  # One month behind
        if current_month < 1:
            current_month = 12
            current_year -= 1
        
        # Generate all months between start and current
        total_start_months = start_year * 12 + start_month
        total_current_months = current_year * 12 + current_month
        
        # Month names for formatting
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        for total_month in range(total_start_months, total_current_months + 1):
            year = total_month // 12
            month = total_month % 12
            if month == 0:
                month = 12
                year -= 1
                
            period_label = f"{month_names[month-1]} {year}"
            periods.append({
                "label": period_label,
                "value": {
                    "month": month,
                    "year": year
                }
            })
    else:
        # For quarterly payments, generate from contract start to current quarter - 1
        # Calculate starting quarter
        start_year = start_date.year
        start_quarter = (start_date.month - 1) // 3 + 1
        
        # Calculate current quarter (with 1 quarter behind for arrears)
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1 - 1  # One quarter behind
        if current_quarter < 1:
            current_quarter = 4
            current_year -= 1
        
        # Generate all quarters between start and current
        total_start_quarters = start_year * 4 + start_quarter
        total_current_quarters = current_year * 4 + current_quarter
        
        for total_quarter in range(total_start_quarters, total_current_quarters + 1):
            year = total_quarter // 4
            quarter = total_quarter % 4
            if quarter == 0:
                quarter = 4
                year -= 1
                
            period_label = f"Q{quarter} {year}"
            periods.append({
                "label": period_label,
                "value": {
                    "quarter": quarter,
                    "year": year
                }
            })
    
    # Make sure we return at least one period
    if not periods:
        # Add current period as fallback
        if is_monthly:
            month = current_date.month
            periods.append({
                "label": f"{month_names[month-1]} {current_date.year}",
                "value": {
                    "month": month,
                    "year": current_date.year
                }
            })
        else:
            current_quarter = (current_date.month - 1) // 3 + 1
            periods.append({
                "label": f"Q{current_quarter} {current_date.year}",
                "value": {
                    "quarter": current_quarter,
                    "year": current_date.year
                }
            })
    
    # Sort periods chronologically (newest first)
    periods.reverse()
    
    return {
        "is_monthly": is_monthly,
        "periods": periods,
        "contract_start_date": contract_start
    }

def format_period_label(is_monthly: bool, period: int, year: int) -> str:
    """
    Format a period for display.
    
    Args:
        is_monthly: Whether this is a monthly period
        period: Month (1-12) or quarter (1-4) number
        year: Year
        
    Returns:
        Formatted period string
    """
    if is_monthly:
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        if 1 <= period <= 12:
            return f"{month_names[period-1]} {year}"
        return f"Month {period} {year}"
    else:
        if 1 <= period <= 4:
            return f"Q{period} {year}"
        return f"Quarter {period} {year}"