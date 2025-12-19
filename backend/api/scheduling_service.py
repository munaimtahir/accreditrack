"""
Scheduling Service for calculating due dates and managing recurring compliance.
"""
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional


def calculate_next_due_date(normalized_frequency: str, reference_date: Optional[date] = None) -> Optional[date]:
    """
    Calculate the next due date based on normalized frequency.
    
    Args:
        normalized_frequency: Normalized frequency string (Daily, Weekly, Monthly, etc.)
        reference_date: Reference date to calculate from (defaults to today)
        
    Returns:
        Next due date or None if frequency is not recognized
    """
    if not normalized_frequency:
        return None
    
    if reference_date is None:
        reference_date = date.today()
    
    freq_lower = normalized_frequency.lower().strip()
    
    # Map frequencies to date calculations
    if freq_lower in ['daily', 'day']:
        return reference_date + timedelta(days=1)
    
    elif freq_lower in ['weekly', 'week']:
        return reference_date + timedelta(weeks=1)
    
    elif freq_lower in ['bi-weekly', 'biweekly', 'fortnightly']:
        return reference_date + timedelta(weeks=2)
    
    elif freq_lower in ['monthly', 'month']:
        return reference_date + relativedelta(months=1)
    
    elif freq_lower in ['quarterly', 'quarter']:
        return reference_date + relativedelta(months=3)
    
    elif freq_lower in ['semi-annually', 'semiannually', 'semi-annual', 'semiannual']:
        return reference_date + relativedelta(months=6)
    
    elif freq_lower in ['annual', 'annually', 'yearly', 'year']:
        return reference_date + relativedelta(years=1)
    
    # If not recognized, return None
    return None


def get_period_dates(normalized_frequency: str, reference_date: Optional[date] = None) -> tuple:
    """
    Get the period start and end dates for a given frequency.
    
    Args:
        normalized_frequency: Normalized frequency string
        reference_date: Reference date (defaults to today)
        
    Returns:
        Tuple of (period_start, period_end)
    """
    if reference_date is None:
        reference_date = date.today()
    
    freq_lower = normalized_frequency.lower().strip()
    
    if freq_lower in ['daily', 'day']:
        return (reference_date, reference_date)
    
    elif freq_lower in ['weekly', 'week']:
        # Start of week (Monday)
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=6)
        return (start, end)
    
    elif freq_lower in ['bi-weekly', 'biweekly', 'fortnightly']:
        # Two-week period
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=13)
        return (start, end)
    
    elif freq_lower in ['monthly', 'month']:
        # Start of month
        start = reference_date.replace(day=1)
        # Last day of month
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1) - timedelta(days=1)
        return (start, end)
    
    elif freq_lower in ['quarterly', 'quarter']:
        # Determine quarter
        quarter = (reference_date.month - 1) // 3
        start_month = quarter * 3 + 1
        start = reference_date.replace(month=start_month, day=1)
        end = start + relativedelta(months=3) - timedelta(days=1)
        return (start, end)
    
    elif freq_lower in ['semi-annually', 'semiannually', 'semi-annual', 'semiannual']:
        # First or second half of year
        if reference_date.month <= 6:
            start = reference_date.replace(month=1, day=1)
            end = reference_date.replace(month=6, day=30)
        else:
            start = reference_date.replace(month=7, day=1)
            end = reference_date.replace(month=12, day=31)
        return (start, end)
    
    elif freq_lower in ['annual', 'annually', 'yearly', 'year']:
        # Calendar year
        start = reference_date.replace(month=1, day=1)
        end = reference_date.replace(month=12, day=31)
        return (start, end)
    
    # Default to single day
    return (reference_date, reference_date)


def is_overdue(due_date: date, current_date: Optional[date] = None) -> bool:
    """
    Check if a due date is overdue.
    
    Args:
        due_date: The due date to check
        current_date: Current date (defaults to today)
        
    Returns:
        True if overdue, False otherwise
    """
    if current_date is None:
        current_date = date.today()
    
    return due_date < current_date


def days_until_due(due_date: date, current_date: Optional[date] = None) -> int:
    """
    Calculate days until due date.
    
    Args:
        due_date: The due date
        current_date: Current date (defaults to today)
        
    Returns:
        Number of days (negative if overdue)
    """
    if current_date is None:
        current_date = date.today()
    
    return (due_date - current_date).days
