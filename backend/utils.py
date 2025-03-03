# backend/utils.py
# Shared utility functions

from datetime import datetime, date
from typing import Optional, Dict, List, Any, Union
import locale
import os
from pathlib import Path

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass  # Fallback to default formatting if locale not available

def format_currency(amount: Optional[Union[float, int]]) -> str:
    """
    Format amount as USD currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted string with $ symbol and commas
    """
    if amount is None:
        return "N/A"
    
    try:
        return locale.currency(float(amount), grouping=True)
    except:
        # Fallback if locale formatting fails
        return f"${amount:,.2f}"

def format_percentage(value: Optional[float]) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Value to format (0.05 = 5%)
        
    Returns:
        Formatted string with % symbol
    """
    if value is None:
        return "N/A"
    
    return f"{value:.2f}%"

def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Date object or None if invalid
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def format_date(date_obj: Optional[Union[date, datetime, str]], format_str: str = '%m/%d/%Y') -> str:
    """
    Format date object to string.
    
    Args:
        date_obj: Date object, datetime object, or ISO date string
        format_str: Format string for strftime
        
    Returns:
        Formatted date string
    """
    if date_obj is None:
        return ""
    
    # If it's a string, try to parse it
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
        if date_obj is None:
            return ""
    
    # If it's a datetime, convert to date
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    return date_obj.strftime(format_str)

def quarter_to_months(quarter: int) -> List[int]:
    """
    Convert quarter number to list of month numbers.
    
    Args:
        quarter: Quarter number (1-4)
        
    Returns:
        List of month numbers
    """
    if quarter < 1 or quarter > 4:
        raise ValueError("Quarter must be between 1 and 4")
    
    start_month = (quarter - 1) * 3 + 1
    return [start_month, start_month + 1, start_month + 2]

def month_to_quarter(month: int) -> int:
    """
    Convert month number to quarter number.
    
    Args:
        month: Month number (1-12)
        
    Returns:
        Quarter number (1-4)
    """
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")
    
    return (month - 1) // 3 + 1

def format_period(is_monthly: bool, period: int, year: int) -> str:
    """
    Format period for display.
    
    Args:
        is_monthly: Whether period is a month
        period: Period number (1-12 for months, 1-4 for quarters)
        year: Year
        
    Returns:
        Formatted period string
    """
    if is_monthly:
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        if period < 1 or period > 12:
            return f"Invalid Month ({period}) {year}"
        return f"{month_names[period-1]} {year}"
    else:
        if period < 1 or period > 4:
            return f"Invalid Quarter ({period}) {year}"
        return f"Q{period} {year}"

def format_applied_period(payment: Dict[str, Any]) -> str:
    """
    Format the applied period from a payment record.
    
    Args:
        payment: Payment dictionary
        
    Returns:
        Formatted period string
    """
    # Determine if monthly or quarterly
    is_monthly = payment.get('applied_start_month') is not None
    
    if is_monthly:
        start_month = payment.get('applied_start_month')
        start_year = payment.get('applied_start_month_year')
        end_month = payment.get('applied_end_month')
        end_year = payment.get('applied_end_month_year')
        
        if start_month == end_month and start_year == end_year:
            return format_period(True, start_month, start_year)
        else:
            start_str = format_period(True, start_month, start_year)
            end_str = format_period(True, end_month, end_year)
            return f"{start_str} - {end_str}"
    else:
        start_quarter = payment.get('applied_start_quarter')
        start_year = payment.get('applied_start_quarter_year')
        end_quarter = payment.get('applied_end_quarter')
        end_year = payment.get('applied_end_quarter_year')
        
        if start_quarter == end_quarter and start_year == end_year:
            return format_period(False, start_quarter, start_year)
        else:
            start_str = format_period(False, start_quarter, start_year)
            end_str = format_period(False, end_quarter, end_year)
            return f"{start_str} - {end_str}"

def normalize_path(path: str) -> str:
    """
    Normalize file path for cross-platform compatibility.
    
    Args:
        path: File path
        
    Returns:
        Normalized path
    """
    if not path:
        return ""
    
    # Convert to Path object and back to string
    normalized = str(Path(path))
    
    # Ensure proper path separators
    return normalized.replace('\\', '/')

def calculate_payment_variance(expected: Optional[float], actual: float) -> Dict[str, Any]:
    """
    Calculate variance between expected and actual payment.
    
    Args:
        expected: Expected payment amount
        actual: Actual payment amount
        
    Returns:
        Dictionary with variance amount, percentage, and status
    """
    if expected is None:
        return {
            "amount": None,
            "percentage": None,
            "status": "unknown"
        }
    
    variance_amount = actual - expected
    variance_percentage = (variance_amount / expected) * 100 if expected != 0 else 0
    
    # Determine status
    if abs(variance_percentage) <= 5:
        status = "ok"
    elif abs(variance_percentage) <= 15:
        status = "warning"
    else:
        status = "error"
    
    return {
        "amount": variance_amount,
        "percentage": variance_percentage,
        "status": status
    }