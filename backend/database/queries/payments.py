# backend/database/queries/payments.py
# Payment-related queries

from database.connection import execute_query, execute_single_query, execute_insert, execute_update, execute_delete
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

def get_client_payments(client_id: int, limit: int = 20, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:

    # First check if client exists
    client_check_query = """
    SELECT client_id FROM clients WHERE client_id = ? AND valid_to IS NULL
    """
    client = execute_single_query(client_check_query, (client_id,))
    if not client:
        return [], 0
        
    count_query = """
    SELECT COUNT(*) as total
    FROM payments
    WHERE client_id = ? AND valid_to IS NULL
    """
    
    query = """
    SELECT 
        p.payment_id,
        p.contract_id,
        p.client_id,
        p.received_date,
        p.total_assets,
        p.expected_fee,
        p.actual_fee,
        p.method,
        p.notes,
        p.split_group_id,
        p.applied_start_month,
        p.applied_start_month_year,
        p.applied_end_month,
        p.applied_end_month_year,
        p.applied_start_quarter,
        p.applied_start_quarter_year,
        p.applied_end_quarter,
        p.applied_end_quarter_year,
        c.display_name as client_name,
        co.provider_name,
        co.fee_type,
        co.percent_rate,
        co.flat_rate,
        co.payment_schedule,
        (SELECT COUNT(*) FROM payment_files pf WHERE pf.payment_id = p.payment_id) as file_count
    FROM 
        payments p
    JOIN 
        clients c ON p.client_id = c.client_id
    LEFT JOIN 
        contracts co ON p.contract_id = co.contract_id
    WHERE 
        p.client_id = ? AND
        p.valid_to IS NULL
    ORDER BY 
        p.received_date DESC
    LIMIT ? OFFSET ?
    """
    
    total_result = execute_single_query(count_query, (client_id,))
    total = total_result['total'] if total_result else 0
    
    payments = execute_query(query, (client_id, limit, offset))
    
    return payments, total

def get_payment_by_id(payment_id: int) -> Optional[Dict[str, Any]]:

    query = """
    SELECT 
        p.payment_id,
        p.contract_id,
        p.client_id,
        p.received_date,
        p.total_assets,
        p.expected_fee,
        p.actual_fee,
        p.method,
        p.notes,
        p.split_group_id,
        p.applied_start_month,
        p.applied_start_month_year,
        p.applied_end_month,
        p.applied_end_month_year,
        p.applied_start_quarter,
        p.applied_start_quarter_year,
        p.applied_end_quarter,
        p.applied_end_quarter_year,
        c.display_name as client_name,
        co.provider_name,
        co.fee_type,
        co.percent_rate,
        co.flat_rate,
        co.payment_schedule
    FROM 
        payments p
    JOIN 
        clients c ON p.client_id = c.client_id
    LEFT JOIN 
        contracts co ON p.contract_id = co.contract_id
    WHERE 
        p.payment_id = ? AND
        p.valid_to IS NULL
    """
    return execute_single_query(query, (payment_id,))

def create_payment(
    contract_id: int,
    client_id: int,
    received_date: str,
    total_assets: Optional[int],
    expected_fee: Optional[float],
    actual_fee: float,
    method: Optional[str],
    notes: Optional[str],
    applied_start_month: Optional[int],
    applied_start_month_year: Optional[int],
    applied_end_month: Optional[int],
    applied_end_month_year: Optional[int],
    applied_start_quarter: Optional[int],
    applied_start_quarter_year: Optional[int],
    applied_end_quarter: Optional[int],
    applied_end_quarter_year: Optional[int],
    split_group_id: Optional[str] = None
) -> int:
    """
    Create a new payment record.
    
    Args:
        All payment fields
        
    Returns:
        ID of the newly created payment
    """
    query = """
    INSERT INTO payments (
        contract_id,
        client_id,
        received_date,
        total_assets,
        expected_fee,
        actual_fee,
        method,
        notes,
        split_group_id,
        applied_start_month,
        applied_start_month_year,
        applied_end_month,
        applied_end_month_year,
        applied_start_quarter,
        applied_start_quarter_year,
        applied_end_quarter,
        applied_end_quarter_year
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        contract_id,
        client_id,
        received_date,
        total_assets,
        expected_fee,
        actual_fee,
        method,
        notes,
        split_group_id,
        applied_start_month,
        applied_start_month_year,
        applied_end_month,
        applied_end_month_year,
        applied_start_quarter,
        applied_start_quarter_year,
        applied_end_quarter,
        applied_end_quarter_year
    )
    
    return execute_insert(query, params)

def create_split_payments(
    contract_id: int,
    client_id: int,
    received_date: str,
    total_assets: Optional[int],
    expected_fee: Optional[float],
    actual_fee: float,
    method: Optional[str],
    notes: Optional[str],
    is_monthly: bool,
    start_period: int,
    start_period_year: int,
    end_period: int,
    end_period_year: int
) -> List[int]:
    # Generate a unique ID for the split payment group
    split_group_id = str(uuid.uuid4())
    
    # Calculate total periods and amount per period
    periods = []
    
    if is_monthly:
        # Calculate months between start and end
        start_total_months = start_period_year * 12 + start_period
        end_total_months = end_period_year * 12 + end_period
        
        # If end is before start, swap them (shouldn't happen with validation)
        if end_total_months < start_total_months:
            start_period, end_period = end_period, start_period
            start_period_year, end_period_year = end_period_year, start_period_year
            start_total_months, end_total_months = end_total_months, start_total_months
        
        num_periods = end_total_months - start_total_months + 1
        
        # Generate all periods between start and end
        for i in range(num_periods):
            total_month = start_total_months + i
            year = total_month // 12
            month = total_month % 12
            if month == 0:
                month = 12
                year -= 1
                
            periods.append({
                'month': month,
                'year': year,
                'quarter': None,
                'quarter_year': None
            })
    else:
        # Calculate quarters between start and end
        start_total_quarters = start_period_year * 4 + start_period
        end_total_quarters = end_period_year * 4 + end_period
        
        # If end is before start, swap them (shouldn't happen with validation)
        if end_total_quarters < start_total_quarters:
            start_period, end_period = end_period, start_period
            start_period_year, end_period_year = end_period_year, start_period_year
            start_total_quarters, end_total_quarters = end_total_quarters, start_total_quarters
        
        num_periods = end_total_quarters - start_total_quarters + 1
        
        # Generate all periods between start and end
        for i in range(num_periods):
            total_quarter = start_total_quarters + i
            year = total_quarter // 4
            quarter = total_quarter % 4
            if quarter == 0:
                quarter = 4
                year -= 1
                
            periods.append({
                'month': None,
                'year': None,
                'quarter': quarter,
                'quarter_year': year
            })
    
    # Calculate payment amount per period (with rounding to two decimal places)
    amount_per_period = round(actual_fee / num_periods, 2)
    
    # Calculate expected fee per period if available
    expected_fee_per_period = None
    if expected_fee is not None:
        expected_fee_per_period = round(expected_fee / num_periods, 2)
    
    # Adjust the last period to account for rounding errors
    last_period_adjustment = round(actual_fee - (amount_per_period * (num_periods - 1)), 2)
    
    payment_ids = []
    
    # Create each period's payment
    for i, period in enumerate(periods):
        # Last period gets the adjustment amount
        period_amount = last_period_adjustment if i == len(periods) - 1 else amount_per_period
        
        payment_id = create_payment(
            contract_id=contract_id,
            client_id=client_id,
            received_date=received_date,
            total_assets=total_assets,
            expected_fee=expected_fee_per_period,
            actual_fee=period_amount,
            method=method,
            notes=notes,
            applied_start_month=period['month'],
            applied_start_month_year=period['year'],
            applied_end_month=period['month'],
            applied_end_month_year=period['year'],
            applied_start_quarter=period['quarter'],
            applied_start_quarter_year=period['quarter_year'],
            applied_end_quarter=period['quarter'],
            applied_end_quarter_year=period['quarter_year'],
            split_group_id=split_group_id
        )
        
        payment_ids.append(payment_id)
    
    return payment_ids

def update_payment(
    payment_id: int,
    received_date: Optional[str] = None,
    total_assets: Optional[int] = None,
    actual_fee: Optional[float] = None,
    method: Optional[str] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Update an existing payment record.
    Only updates fields that are provided (not None).
    
    Args:
        payment_id: ID of payment to update
        Other fields optional
        
    Returns:
        True if update successful, False otherwise
    """
    # Build dynamic query based on which fields are provided
    update_fields = []
    params = []
    
    if received_date is not None:
        update_fields.append("received_date = ?")
        params.append(received_date)
    
    if total_assets is not None:
        update_fields.append("total_assets = ?")
        params.append(total_assets)
    
    if actual_fee is not None:
        update_fields.append("actual_fee = ?")
        params.append(actual_fee)
    
    if method is not None:
        update_fields.append("method = ?")
        params.append(method)
    
    if notes is not None:
        update_fields.append("notes = ?")
        params.append(notes)
    
    # If no fields to update, return early
    if not update_fields:
        return False
    
    # Add payment_id to params
    params.append(payment_id)
    
    query = f"""
    UPDATE payments
    SET {", ".join(update_fields)}
    WHERE payment_id = ? AND valid_to IS NULL
    """
    
    rows_updated = execute_update(query, tuple(params))
    return rows_updated > 0

def update_expected_fee(payment_id: int, expected_fee: float) -> bool:
    """
    Update the expected fee for a payment.
    
    Args:
        payment_id: ID of payment to update
        expected_fee: New expected fee
        
    Returns:
        True if update successful, False otherwise
    """
    query = """
    UPDATE payments
    SET expected_fee = ?
    WHERE payment_id = ? AND valid_to IS NULL
    """
    
    rows_updated = execute_update(query, (expected_fee, payment_id))
    return rows_updated > 0

def delete_payment(payment_id: int) -> bool:
    """
    Soft delete a payment by setting valid_to timestamp.
    
    Args:
        payment_id: ID of payment to delete
        
    Returns:
        True if deletion successful, False otherwise
    """
    query = """
    UPDATE payments
    SET valid_to = datetime('now')
    WHERE payment_id = ? AND valid_to IS NULL
    """
    
    rows_updated = execute_update(query, (payment_id,))
    return rows_updated > 0

def get_split_payment_group(split_group_id: str) -> List[Dict[str, Any]]:
    """
    Get all payments in a split payment group.
    
    Args:
        split_group_id: UUID of the split payment group
        
    Returns:
        List of payments in the group
    """
    query = """
    SELECT 
        payment_id,
        contract_id,
        client_id,
        received_date,
        total_assets,
        expected_fee,
        actual_fee,
        method,
        notes,
        split_group_id,
        applied_start_month,
        applied_start_month_year,
        applied_end_month,
        applied_end_month_year,
        applied_start_quarter,
        applied_start_quarter_year,
        applied_end_quarter,
        applied_end_quarter_year
    FROM 
        payments
    WHERE 
        split_group_id = ? AND
        valid_to IS NULL
    ORDER BY 
        COALESCE(applied_start_month_year, applied_start_quarter_year),
        COALESCE(applied_start_month, applied_start_quarter)
    """
    
    return execute_query(query, (split_group_id,))

def calculate_expected_fee(contract_id: int, total_assets: Optional[int], period_type: str) -> Optional[float]:
    """
    Calculate expected fee based on contract and assets.
    Args:
        contract_id: Contract ID
        total_assets: Total assets amount (can be None for flat fee)
        period_type: 'month' or 'quarter'
    Returns:
        Expected fee amount or None if not enough information
    """
    query = """
    SELECT 
        fee_type,
        percent_rate,
        flat_rate,
        payment_schedule
    FROM 
        contracts
    WHERE 
        contract_id = ? AND
        valid_to IS NULL
    """
    contract = execute_single_query(query, (contract_id,))
    if not contract:
        return None
    
    # Normalize period type to match database terminology
    period_type_normalized = 'monthly' if period_type == 'month' else 'quarterly' if period_type == 'quarter' else period_type
    
    fee_type = contract['fee_type'].lower() if contract['fee_type'] else None
    # Handle flat fee
    if fee_type == 'flat':
        flat_rate = contract['flat_rate']
        if flat_rate is None:
            return None
        # Return full flat rate if periods match, otherwise adjust
        if contract['payment_schedule'] == period_type_normalized:
            return flat_rate
        elif contract['payment_schedule'] == 'monthly' and period_type_normalized == 'quarterly':
            return flat_rate * 3
        elif contract['payment_schedule'] == 'quarterly' and period_type_normalized == 'monthly':
            return flat_rate / 3
    # Handle percentage fee
    elif fee_type in ('percentage', 'percent'):
        percent_rate = contract['percent_rate']
        if percent_rate is None or total_assets is None:
            return None
        # Apply percentage rate to assets
        # Note: percent_rate is already stored as a decimal in the database (e.g., 0.005 for 0.5%)
        decimal_rate = float(percent_rate)
        # Apply rate based on period type
        if contract['payment_schedule'] == period_type_normalized:
            return total_assets * decimal_rate
        elif contract['payment_schedule'] == 'monthly' and period_type_normalized == 'quarterly':
            return total_assets * decimal_rate * 3
        elif contract['payment_schedule'] == 'quarterly' and period_type_normalized == 'monthly':
            return total_assets * decimal_rate / 3
    # Default case if calculation not possible
    return None

def get_payment_files(payment_id: int) -> List[Dict[str, Any]]:
    """
    Get files associated with a payment.
    
    Args:
        payment_id: Payment ID
        
    Returns:
        List of file dictionaries
    """
    query = """
    SELECT 
        cf.file_id,
        cf.client_id,
        cf.file_name,
        cf.onedrive_path,
        cf.uploaded_at,
        pf.linked_at
    FROM 
        client_files cf
    JOIN 
        payment_files pf ON cf.file_id = pf.file_id
    WHERE 
        pf.payment_id = ?
    ORDER BY 
        pf.linked_at DESC
    """
    
    return execute_query(query, (payment_id,))