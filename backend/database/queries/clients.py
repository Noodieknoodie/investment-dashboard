# backend/database/queries/clients.py
# Client-related queries
from database.connection import execute_query, execute_single_query
from typing import List, Dict, Any, Optional
import datetime
def get_all_clients() -> List[Dict[str, Any]]:
    query = """
        SELECT client_id, display_name, full_name, ima_signed_date, onedrive_folder_path
        FROM clients
        WHERE valid_to IS NULL
        ORDER BY display_name
    """
    return execute_query(query)
	
def get_client_by_id(client_id: int) -> Optional[Dict[str, Any]]:
 
    query = """
        SELECT client_id, display_name, full_name, ima_signed_date, onedrive_folder_path
        FROM clients
        WHERE client_id = ? AND valid_to IS NULL
    """
    return execute_single_query(query, (client_id,))
	
def get_client_with_contracts(client_id: int) -> Optional[Dict[str, Any]]:
    # Get the client
    client = get_client_by_id(client_id)
    if not client:
        return None
    
    # Get client's contracts
    query = """
        SELECT 
            contract_id, client_id, contract_number, provider_name,
            contract_start_date, fee_type, percent_rate, flat_rate,
            payment_schedule, num_people, notes
        FROM contracts
        WHERE client_id = ? AND valid_to IS NULL
        ORDER BY contract_start_date DESC
    """
    contracts = execute_query(query, (client_id,))
    
    # Add contracts to client data
    client['contracts'] = contracts
    return client
	
def get_clients_by_provider() -> List[Dict[str, Any]]:
    query = """
        SELECT 
            c.client_id, 
            c.display_name, 
            c.full_name, 
            con.provider_name
        FROM clients c
        LEFT JOIN contracts con ON c.client_id = con.client_id AND con.valid_to IS NULL
        WHERE c.valid_to IS NULL
        ORDER BY con.provider_name, c.display_name
    """
    return execute_query(query)
	
def get_client_metrics(client_id: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT 
            client_id, last_payment_date, last_payment_amount,
            last_payment_quarter, last_payment_year, total_ytd_payments,
            avg_quarterly_payment, last_recorded_assets
        FROM client_metrics
        WHERE client_id = ?
    """
    return execute_single_query(query, (client_id,))
	
def get_client_compliance_status(client_id: int) -> Dict[str, str]:
    # Get last payment information
    query = """
        SELECT 
            received_date, 
            payment_schedule,
            CASE 
                WHEN applied_start_quarter IS NOT NULL THEN applied_start_quarter
                ELSE applied_start_month
            END as applied_period,
            CASE 
                WHEN applied_start_quarter_year IS NOT NULL THEN applied_start_quarter_year
                ELSE applied_start_month_year
            END as applied_period_year
        FROM payments p
        JOIN contracts c ON p.contract_id = c.contract_id
        WHERE p.client_id = ? AND p.valid_to IS NULL
        ORDER BY p.received_date DESC
        LIMIT 1
    """
    last_payment = execute_single_query(query, (client_id,))
    
    if not last_payment:
        return {
            "status": "red",
            "reason": "No payment records found"
        }
    
    # Parse the last payment date
    try:
        last_payment_date = datetime.datetime.strptime(
            last_payment['received_date'], '%Y-%m-%d'
        ).date()
    except ValueError:
        return {
            "status": "red",
            "reason": "Invalid payment date format"
        }
    
    # Get today's date for comparison
    today = datetime.date.today()
    
    # Calculate days since last payment
    days_since_payment = (today - last_payment_date).days
    
    # Check if it's a monthly or quarterly payment schedule
    is_monthly = last_payment['payment_schedule'] == 'monthly'
    
    # Determine compliance status based on payment schedule
    if is_monthly:
        if days_since_payment <= 45:  # Within 1.5 months
            return {
                "status": "green",
                "reason": "Recent payment within acceptable timeframe"
            }
        elif days_since_payment <= 75:  # Within 2.5 months
            return {
                "status": "yellow",
                "reason": "Payment approaching due date"
            }
        else:
            return {
                "status": "red",
                "reason": "Payment overdue"
            }
    else:  # Quarterly
        if days_since_payment <= 135:  # Within 4.5 months
            return {
                "status": "green",
                "reason": "Recent payment within acceptable timeframe"
            }
        elif days_since_payment <= 195:  # Within 6.5 months
            return {
                "status": "yellow",
                "reason": "Payment approaching due date"
            }
        else:
            return {
                "status": "red",
                "reason": "Payment overdue"
            }
			
def get_quarterly_summary(client_id: int, year: int, quarter: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT 
            id, client_id, year, quarter, total_payments, 
            total_assets, payment_count, avg_payment, 
            expected_total, last_updated
        FROM quarterly_summaries
        WHERE client_id = ? AND year = ? AND quarter = ?
    """
    return execute_single_query(query, (client_id, year, quarter))
	
def get_yearly_summary(client_id: int, year: int) -> Optional[Dict[str, Any]]:
    query = """
        SELECT 
            id, client_id, year, total_payments, total_assets, 
            payment_count, avg_payment, yoy_growth, last_updated
        FROM yearly_summaries
        WHERE client_id = ? AND year = ?
    """
    return execute_single_query(query, (client_id, year))
	
def update_client_folder_path(client_id: int, folder_path: str) -> bool:
    from database.connection import execute_update
    
    # Normalize path (ensure consistent format)
    normalized_path = folder_path.replace('/', '\\')
    
    query = """
        UPDATE clients
        SET onedrive_folder_path = ?
        WHERE client_id = ? AND valid_to IS NULL
    """
    
    rows_updated = execute_update(query, (normalized_path, client_id))
    return rows_updated > 0