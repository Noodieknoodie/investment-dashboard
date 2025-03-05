"""
Tests for payment query functionality.
"""
import pytest
from datetime import datetime
import uuid
from database.queries import payments as payment_queries

def test_get_client_payments(test_client_id):
    """
    Test that get_client_payments returns payments for a client.
    """
    payments, total = payment_queries.get_client_payments(test_client_id, 5, 0)
    assert isinstance(payments, list), "Payments should be a list"
    assert isinstance(total, int), "Total should be an integer"
    assert total >= len(payments), "Total should be at least as large as returned payments"

def test_get_payment_by_id():
    """
    Test that get_payment_by_id returns a payment if it exists.
    """
    # Get a payment ID first
    test_client_id = 1
    payments, _ = payment_queries.get_client_payments(test_client_id, 1, 0)
    
    # Skip if no payments found
    if not payments:
        pytest.skip("No payments found for testing")
    
    payment_id = payments[0]['payment_id']
    payment = payment_queries.get_payment_by_id(payment_id)
    
    assert payment is not None, "Payment should not be None"
    assert payment['payment_id'] == payment_id, "Payment ID should match requested ID"
    assert 'client_name' in payment, "Payment should include client_name"

@pytest.mark.parametrize("is_monthly", [True, False])
def test_create_and_delete_payment(test_client_id, test_contract_id, is_monthly):
    """
    Test that create_payment creates a payment and delete_payment deletes it.
    """
    # Create test payment data
    today = datetime.now().strftime('%Y-%m-%d')
    
    if is_monthly:
        # Monthly payment
        payment_id = payment_queries.create_payment(
            contract_id=test_contract_id,
            client_id=test_client_id,
            received_date=today,
            total_assets=100000,
            expected_fee=1000.0,
            actual_fee=1000.0,
            method="Test",
            notes="Test payment - PLEASE DELETE",
            applied_start_month=1,
            applied_start_month_year=2023,
            applied_end_month=1,
            applied_end_month_year=2023,
            applied_start_quarter=None,
            applied_start_quarter_year=None,
            applied_end_quarter=None,
            applied_end_quarter_year=None
        )
    else:
        # Quarterly payment
        payment_id = payment_queries.create_payment(
            contract_id=test_contract_id,
            client_id=test_client_id,
            received_date=today,
            total_assets=100000,
            expected_fee=1000.0,
            actual_fee=1000.0,
            method="Test",
            notes="Test payment - PLEASE DELETE",
            applied_start_month=None,
            applied_start_month_year=None,
            applied_end_month=None,
            applied_end_month_year=None,
            applied_start_quarter=1,
            applied_start_quarter_year=2023,
            applied_end_quarter=1,
            applied_end_quarter_year=2023
        )
    
    assert payment_id > 0, "Payment ID should be positive"
    
    # Verify payment was created
    payment = payment_queries.get_payment_by_id(payment_id)
    assert payment is not None, "Payment should not be None"
    assert payment['payment_id'] == payment_id, "Payment ID should match created ID"
    
    # Delete payment
    deleted = payment_queries.delete_payment(payment_id)
    assert deleted is True, "Delete payment should return True"
    
    # Verify payment was deleted (soft delete)
    payment = payment_queries.get_payment_by_id(payment_id)
    assert payment is None, "Payment should be None after deletion"

def test_update_payment(test_client_id, test_contract_id):
    """
    Test that update_payment updates a payment.
    """
    # Create a payment to update
    today = datetime.now().strftime('%Y-%m-%d')
    payment_id = payment_queries.create_payment(
        contract_id=test_contract_id,
        client_id=test_client_id,
        received_date=today,
        total_assets=100000,
        expected_fee=1000.0,
        actual_fee=1000.0,
        method="Test",
        notes="Original test payment",
        applied_start_month=1,
        applied_start_month_year=2023,
        applied_end_month=1,
        applied_end_month_year=2023,
        applied_start_quarter=None,
        applied_start_quarter_year=None,
        applied_end_quarter=None,
        applied_end_quarter_year=None
    )
    
    # Update the payment
    updated = payment_queries.update_payment(
        payment_id=payment_id,
        notes="Updated test payment"
    )
    assert updated is True, "Update payment should return True"
    
    # Verify payment was updated
    payment = payment_queries.get_payment_by_id(payment_id)
    assert payment['notes'] == "Updated test payment", "Payment notes should be updated"
    
    # Clean up
    payment_queries.delete_payment(payment_id)


def test_calculate_expected_fee(test_contract_id):
    """
    Test that calculate_expected_fee calculates the expected fee.
    """
    # Test with monthly period
    monthly_fee = payment_queries.calculate_expected_fee(test_contract_id, 100000, 'month')
    
    # Test with quarterly period
    quarterly_fee = payment_queries.calculate_expected_fee(test_contract_id, 100000, 'quarter')
    
    # One of these may be None depending on contract type
    assert monthly_fee is not None or quarterly_fee is not None, "At least one fee should be calculated"
    
    # If both are calculated, quarterly should be about 3x monthly
    if monthly_fee is not None and quarterly_fee is not None:
        # Allow for small rounding differences
        assert abs(quarterly_fee - (monthly_fee * 3)) < 0.01, "Quarterly fee should be about 3x monthly fee"