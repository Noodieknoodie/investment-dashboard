# backend/services/client_service.py
# Client-related business logic

from database.queries import clients as client_queries
from typing import List, Dict, Any, Optional
from models.schemas import Client, ClientSnapshot, Contract, ClientMetrics

def get_all_clients() -> List[Client]:

    client_data = client_queries.get_all_clients()
    return [Client(**client) for client in client_data]

def get_clients_by_provider() -> List[Dict[str, Any]]:

    clients = client_queries.get_clients_by_provider()
    
    # Group clients by provider
    grouped = {}
    for client in clients:
        provider = client.get('provider_name') or 'No Provider'
        if provider not in grouped:
            grouped[provider] = []
        
        grouped[provider].append({
            'client_id': client['client_id'],
            'display_name': client['display_name'],
            'full_name': client['full_name']
        })
    
    # Convert to list format for frontend
    result = []
    for provider, provider_clients in grouped.items():
        result.append({
            'provider': provider,
            'clients': provider_clients
        })
    
    return result

def get_client_snapshot(client_id: int) -> Optional[ClientSnapshot]:

    # Get client and contract data
    client_data = client_queries.get_client_with_contracts(client_id)
    if not client_data:
        return None
    
    # Get metrics data
    metrics_data = client_queries.get_client_metrics(client_id)
    
    # Extract client and contracts
    client = Client(
        client_id=client_data['client_id'],
        display_name=client_data['display_name'],
        full_name=client_data['full_name'],
        ima_signed_date=client_data['ima_signed_date'],
        onedrive_folder_path=client_data['onedrive_folder_path']
    )
    
    contracts = [Contract(**contract) for contract in client_data['contracts']]
    
    # Create metrics if available
    metrics = ClientMetrics(**metrics_data) if metrics_data else None
    
    # Create and return snapshot
    return ClientSnapshot(
        client=client,
        contracts=contracts,
        metrics=metrics
    )

def get_client_compliance_status(client_id: int) -> Dict[str, str]:

    return client_queries.get_client_compliance_status(client_id)

def calculate_fee_summary(client_id: int) -> Dict[str, Any]:

    # Get client contracts
    client_data = client_queries.get_client_with_contracts(client_id)
    if not client_data or not client_data['contracts']:
        return {
            'monthly': None,
            'quarterly': None,
            'annual': None,
            'fee_type': None,
            'rate': None
        }
    
    # Use first active contract
    contract = client_data['contracts'][0]
    fee_type = contract['fee_type'].lower() if contract['fee_type'] else None
    
    # Calculate fees based on type
    if fee_type == 'flat':
        flat_rate = contract['flat_rate']
        if flat_rate is None:
            return {
                'monthly': None,
                'quarterly': None,
                'annual': None,
                'fee_type': 'flat',
                'rate': None
            }
        
        # Calculate monthly, quarterly and annual equivalents
        if contract['payment_schedule'] == 'monthly':
            monthly = flat_rate
            quarterly = monthly * 3
            annual = monthly * 12
        else:  # quarterly
            quarterly = flat_rate
            monthly = quarterly / 3
            annual = quarterly * 4
            
    elif fee_type in ('percentage', 'percent'):
        percent_rate = contract['percent_rate']
        if percent_rate is None:
            return {
                'monthly': None,
                'quarterly': None,
                'annual': None,
                'fee_type': 'percentage',
                'rate': percent_rate
            }
        
        # Get most recent AUM
        metrics_data = client_queries.get_client_metrics(client_id)
        if not metrics_data or metrics_data['last_recorded_assets'] is None:
            return {
                'monthly': None,
                'quarterly': None,
                'annual': None,
                'fee_type': 'percentage',
                'rate': percent_rate
            }
        
        last_assets = metrics_data['last_recorded_assets']
        decimal_rate = float(percent_rate) / 100.0
        
        # Calculate fees based on schedule and rate
        if contract['payment_schedule'] == 'monthly':
            monthly = last_assets * decimal_rate
            quarterly = monthly * 3
            annual = monthly * 12
        else:  # quarterly
            quarterly = last_assets * decimal_rate
            monthly = quarterly / 3
            annual = quarterly * 4
    else:
        # Unknown fee type
        return {
            'monthly': None,
            'quarterly': None,
            'annual': None,
            'fee_type': fee_type,
            'rate': None
        }
            
    return {
        'monthly': round(monthly, 2) if 'monthly' in locals() else None,
        'quarterly': round(quarterly, 2) if 'quarterly' in locals() else None,
        'annual': round(annual, 2) if 'annual' in locals() else None,
        'fee_type': fee_type,
        'rate': contract['percent_rate'] if fee_type in ('percentage', 'percent') else contract['flat_rate']
    }

def update_client_folder_path(client_id: int, folder_path: str) -> Dict[str, Any]:
    """
    Update a client's OneDrive folder path.
    
    Args:
        client_id: ID of the client
        folder_path: New folder path to use
        
    Returns:
        Dictionary with update status
    """
    # Check if client exists
    client = client_queries.get_client_by_id(client_id)
    if not client:
        return {
            "success": False,
            "message": "Client not found"
        }
    
    # Update folder path
    success = client_queries.update_client_folder_path(client_id, folder_path)
    
    if not success:
        return {
            "success": False,
            "message": "Failed to update client folder path"
        }
    
    return {
        "success": True,
        "client_id": client_id,
        "folder_path": folder_path
    }