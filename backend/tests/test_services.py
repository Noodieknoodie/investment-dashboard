"""
Tests for service layer functionality.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from services import client_service, payment_service
from models.schemas import PaymentCreate, PaymentUpdate

def test_get_all_clients():
    """
    Test that get_all_clients service returns a list of Client objects.
    """
    clients = client_service.get_all_clients()
    assert len(clients) > 0, "Should return at least one client"
    
    # Check that the returned objects have the expected attributes
    for client in clients:
        assert hasattr(client, 'client_id'), "Client should have client_id attribute"
        assert hasattr(client, 'display_name'), "Client should have display_name attribute"

def test_get_clients_by_provider():
    """
    Test that get_clients_by_provider service returns clients grouped by provider.
    """
    provider_groups = client_service.get_clients_by_provider()
    assert len(provider_groups) > 0, "Should return at least one provider group"
    
    # Check that the returned data has the expected structure
    for group in provider_groups:
        assert 'provider' in group, "Group should have provider key"
        assert 'clients' in group, "Group should have clients key"
        assert isinstance(group['clients'], list), "Clients should be a list"

def test_get_client_snapshot(test_client_id):
    """
    Test that get_client_snapshot service returns a complete client snapshot.
    """
    snapshot = client_service.get_client_snapshot(test_client_id)
    assert snapshot is not None, "Snapshot should not be None"
    
    # Check client data
    assert hasattr(snapshot.client, 'client_id'), "Client should have client_id attribute"
    assert snapshot.client.client_id == test_client_id, "Client ID should match requested ID"
    
    # Contracts list should exist (may be empty)
    assert hasattr(snapshot, 'contracts'), "Snapshot should have contracts attribute"

def test_get_client_compliance_status(test_client_id):
    """
    Test that get_client_compliance_status service returns compliance status.
    """
    status = client_service.get_client_compliance_status(test_client_id)
    assert 'status' in status, "Status should have status key"
    assert 'reason' in status, "Status should have reason key"
    
    # Status should be one of the valid values
    assert status['status'] in ['green', 'yellow', 'red', 'gray'], "Status should be a valid value"

def test_calculate_fee_summary(test_client_id):
    """
    Test that calculate_fee_summary service returns fee summary data.
    """
    fee_summary = client_service.calculate_fee_summary(test_client_id)
    assert 'fee_type' in fee_summary, "Fee summary should have fee_type key"
    
    # Check that fee fields exist
    assert 'monthly' in fee_summary, "Fee summary should have monthly key"
    assert 'quarterly' in fee_summary, "Fee summary should have quarterly key"
    assert 'annual' in fee_summary, "Fee summary should have annual key"

def test_get_client_payments(test_client_id):
    """
    Test that get_client_payments service returns paginated payment data.
    """
    paginated = payment_service.get_client_payments(test_client_id)
    assert hasattr(paginated, 'total'), "Result should have total attribute"
    assert hasattr(paginated, 'items'), "Result should have items attribute"
    assert hasattr(paginated, 'page'), "Result should have page attribute"
    assert hasattr(paginated, 'page_size'), "Result should have page_size attribute"

def test_create_and_delete_payment(test_client_id, test_contract_id):
    """
    Test creating and deleting a payment through the service layer.
    """
    # Create payment data
    payment_data = PaymentCreate(
        contract_id=test_contract_id,
        client_id=test_client_id,
        received_date=datetime.now().strftime('%Y-%m-%d'),
        actual_fee=Decimal('1000.00'),
        total_assets=100000,
        method="Test",
        notes="Test payment via service layer",
        is_split_payment=False,
        start_period=1,
        start_period_year=2023
    )
    
    # Create payment
    result = payment_service.create_payment(payment_data)
    assert result['success'] is True, "Create payment should succeed"
    assert 'payment_id' in result, "Result should include payment_id"
    
    payment_id = result['payment_id']
    
    # Get payment details
    payment = payment_service.get_payment_by_id(payment_id)
    assert payment is not None, "Payment should exist"
    assert payment.payment_id == payment_id, "Payment ID should match"
    
    # Delete payment
    delete_result = payment_service.delete_payment(payment_id)
    assert delete_result['success'] is True, "Delete payment should succeed"

def test_calculate_expected_fee(test_client_id, test_contract_id):
    """
    Test that calculate_expected_fee service calculates expected fees.
    """
    # Calculate for a month
    monthly_result = payment_service.calculate_expected_fee(
        client_id=test_client_id,
        contract_id=test_contract_id,
        total_assets=100000,
        period_type='month',
        period=1,
        year=2023
    )
    
    assert 'expected_fee' in monthly_result, "Result should include expected_fee"
    assert 'fee_type' in monthly_result, "Result should include fee_type"
    assert 'calculation_method' in monthly_result, "Result should include calculation_method"

def test_get_available_periods(test_client_id, test_contract_id):
    """
    Test that get_available_periods service returns available periods.
    """
    result = payment_service.get_available_periods(test_client_id, test_contract_id)
    assert 'is_monthly' in result, "Result should include is_monthly flag"
    assert 'periods' in result, "Result should include periods list"
    assert 'contract_start_date' in result, "Result should include contract_start_date"
    
    # Periods should be a list of objects with label and value
    if result['periods']:
        period = result['periods'][0]
        assert 'label' in period, "Period should include label"
        assert 'value' in period, "Period should include value"