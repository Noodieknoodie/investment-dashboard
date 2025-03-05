# backend/database/queries/payments.py
# Payment-related queries

from database.connection import execute_query, execute_single_query, execute_insert, execute_update, execute_delete
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

def get_client_payments(client_id: int, limit: int = 20, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """
    Fetch payments for a client with pagination.
    
    Args:
        client_id: Client ID to fetch payments for
        limit: Number of records to return
        offset: Offset for pagination
        
    Returns:
        Tuple of (list of payment dictionaries, total count)
    """
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
    """
    Fetch a single payment by ID with client and contract details.
    
    Args:
        payment_id: Payment ID to fetch
        
    Returns:
        Payment dictionary or None if not found
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
    applied_end_quarter_year: Optional[int]
) -> int:
    """
    Create a new payment record.
    For split payments, start and end period fields differ.
    
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
        applied_start_month,
        applied_start_month_year,
        applied_end_month,
        applied_end_month_year,
        applied_start_quarter,
        applied_start_quarter_year,
        applied_end_quarter,
        applied_end_quarter_year
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    
    fee_type = contract['fee_type'].lower() if contract['fee_type'] else None
    
    # Handle flat fee
    if fee_type == 'flat':
        flat_rate = contract['flat_rate']
        if flat_rate is None:
            return None
        
        # Return full flat rate if periods match, otherwise adjust
        if contract['payment_schedule'] == period_type or (
            contract['payment_schedule'] == 'quarterly' and period_type == 'quarter'):
            return flat_rate
        elif contract['payment_schedule'] == 'monthly' and period_type == 'quarter':
            return flat_rate * 3
        elif contract['payment_schedule'] == 'quarterly' and period_type == 'month':
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
        if contract['payment_schedule'] == period_type or (
            contract['payment_schedule'] == 'quarterly' and period_type == 'quarter'):
            return total_assets * decimal_rate
        elif contract['payment_schedule'] == 'monthly' and period_type == 'quarter':
            return total_assets * decimal_rate * 3
        elif contract['payment_schedule'] == 'quarterly' and period_type == 'month':
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
        f.file_id,
        f.client_id,
        f.file_name,
        f.onedrive_path,
        f.uploaded_at
    FROM 
        client_files f
    JOIN 
        payment_files pf ON f.file_id = pf.file_id
    WHERE 
        pf.payment_id = ?
    """
    
    return execute_query(query, (payment_id,))

def associate_file_with_payment(payment_id: int, file_id: int) -> bool:
    """
    Associate a file with a payment.
    
    Args:
        payment_id: Payment ID
        file_id: File ID
        
    Returns:
        True if association successful, False otherwise
    """
    # Check if already associated
    check_query = """
    SELECT payment_id FROM payment_files WHERE payment_id = ? AND file_id = ?
    """
    existing = execute_single_query(check_query, (payment_id, file_id))
    if existing:
        return True  # Already associated
    
    query = """
    INSERT INTO payment_files (payment_id, file_id) VALUES (?, ?)
    """
    
    try:
        execute_insert(query, (payment_id, file_id))
        return True
    except Exception:
        return False

def disassociate_file_from_payment(payment_id: int, file_id: int) -> bool:
    """
    Remove association between a file and a payment.
    
    Args:
        payment_id: Payment ID
        file_id: File ID
        
    Returns:
        True if disassociation successful, False otherwise
    """
    query = """
    DELETE FROM payment_files WHERE payment_id = ? AND file_id = ?
    """
    
    rows_deleted = execute_delete(query, (payment_id, file_id))
    return rows_deleted > 0

def get_payments_by_period(
    client_id: int, 
    is_monthly: bool, 
    period: int, 
    year: int
) -> List[Dict[str, Any]]:
    """
    Get all payments for a specific period (month or quarter).
    
    Args:
        client_id: Client ID
        is_monthly: True for monthly, False for quarterly
        period: Month or quarter number
        year: Year
        
    Returns:
        List of payment dictionaries
    """
    if is_monthly:
        query = """
        SELECT 
            payment_id,
            contract_id,
            received_date,
            total_assets,
            expected_fee,
            actual_fee,
            method,
            notes,
            applied_start_month,
            applied_start_month_year,
            applied_end_month,
            applied_end_month_year
        FROM 
            payments
        WHERE 
            client_id = ? AND
            ((applied_start_month <= ? AND applied_end_month >= ? AND
              applied_start_month_year = ? AND applied_end_month_year = ?)
             OR
             (applied_start_month_year < ? AND applied_end_month_year > ?)
             OR
             (applied_start_month_year = ? AND applied_end_month_year > ? AND
              applied_start_month <= ?)
             OR
             (applied_start_month_year < ? AND applied_end_month_year = ? AND
              applied_end_month >= ?)) AND
            valid_to IS NULL
        """
        params = (
            client_id, 
            period, period, year, year,
            year, year,
            year, year, period,
            year, year, period
        )
    else:
        query = """
        SELECT 
            payment_id,
            contract_id,
            received_date,
            total_assets,
            expected_fee,
            actual_fee,
            method,
            notes,
            applied_start_quarter,
            applied_start_quarter_year,
            applied_end_quarter,
            applied_end_quarter_year
        FROM 
            payments
        WHERE 
            client_id = ? AND
            ((applied_start_quarter <= ? AND applied_end_quarter >= ? AND
              applied_start_quarter_year = ? AND applied_end_quarter_year = ?)
             OR
             (applied_start_quarter_year < ? AND applied_end_quarter_year > ?)
             OR
             (applied_start_quarter_year = ? AND applied_end_quarter_year > ? AND
              applied_start_quarter <= ?)
             OR
             (applied_start_quarter_year < ? AND applied_end_quarter_year = ? AND
              applied_end_quarter >= ?)) AND
            valid_to IS NULL
        """
        params = (
            client_id, 
            period, period, year, year,
            year, year,
            year, year, period,
            year, year, period
        )
    
    return execute_query(query, params)