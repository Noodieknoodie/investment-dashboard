"""
Test script to verify fee calculations after the fix.
Run with: python -m backend.test_fee_calculation
"""

def test_fee_calculation():
    """Test fee calculation with the given values."""
    total_assets = 2945059
    percent_rate = 0.00067  # The rate as stored in the database
    
    print(f"Testing with:\n - AUM: ${total_assets:,.2f}\n - Rate: {percent_rate:.6f} ({percent_rate*100:.3f}%)")
    
    # Direct calculation with no period adjustments
    expected_fee = total_assets * percent_rate
    
    print("\nStraight Calculation Result:")
    print(f"Expected Fee: ${expected_fee:.2f}")
    
    # User's expected amount
    user_expected = 1963.34
    
    print("\nUser's Expected Value:")
    print(f"Expected Fee: ${user_expected:.2f}")
    
    # Calculate difference
    print("\nDifference:")
    print(f"Difference: ${expected_fee - user_expected:.2f} ({(expected_fee - user_expected)/user_expected*100:.2f}%)")
    
    # Sanity check - see if user's expected value can be derived directly
    calculated_rate = user_expected / total_assets
    print(f"\nRate calculated from expected value: {calculated_rate:.8f} ({calculated_rate*100:.4f}%)")

def main():
    test_fee_calculation()

if __name__ == "__main__":
    main() 