"""
Compliance Service for frequency-based evidence tracking and compliance calculation.
"""
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from django.db.models import Q, Count
from django.utils import timezone
from .models import Indicator, Evidence, EvidencePeriod, FrequencyLog
from .scheduling_service import get_period_dates, calculate_next_due_date


def calculate_compliance_status(indicator: Indicator) -> Dict[str, any]:
    """
    Calculate compliance status for an indicator based on evidence periods.
    
    Args:
        indicator: Indicator instance
        
    Returns:
        Dict with compliance status, missing periods, and statistics
    """
    if indicator.schedule_type != 'recurring' or not indicator.normalized_frequency:
        # For one-time indicators, check if any evidence exists
        evidence_count = indicator.evidence.count()
        return {
            'status': 'compliant' if evidence_count > 0 else 'not_compliant',
            'evidence_count': evidence_count,
            'missing_periods': [],
            'last_submitted': indicator.evidence.order_by('-uploaded_at').first().uploaded_at.date() if evidence_count > 0 else None,
            'next_due_date': None
        }
    
    # For recurring indicators, check period coverage
    today = date.today()
    frequency = indicator.normalized_frequency
    
    # Get all expected periods from indicator creation to now
    expected_periods = _get_expected_periods(indicator, frequency, today)
    
    # Get actual evidence periods
    actual_periods = _get_actual_evidence_periods(indicator)
    
    # Find missing periods
    missing_periods = _find_missing_periods(expected_periods, actual_periods)
    
    # Calculate compliance status
    if len(missing_periods) == 0:
        status = 'compliant'
    elif len(missing_periods) < len(expected_periods):
        status = 'in_process'
    else:
        status = 'not_compliant'
    
    # Get last submitted date
    last_evidence = indicator.evidence.order_by('-uploaded_at').first()
    last_submitted = last_evidence.uploaded_at.date() if last_evidence else None
    
    # Calculate next due date
    next_due = calculate_next_due_date(frequency, today)
    
    return {
        'status': status,
        'evidence_count': len(actual_periods),
        'expected_count': len(expected_periods),
        'missing_periods': missing_periods,
        'last_submitted': last_submitted,
        'next_due_date': next_due,
        'coverage_percentage': (len(actual_periods) / len(expected_periods) * 100) if expected_periods else 0
    }


def get_missing_periods(indicator: Indicator, end_date: Optional[date] = None) -> List[Dict[str, date]]:
    """
    Get list of missing evidence periods for an indicator.
    
    Args:
        indicator: Indicator instance
        end_date: End date for period calculation (defaults to today)
        
    Returns:
        List of dicts with 'start' and 'end' dates for missing periods
    """
    if indicator.schedule_type != 'recurring' or not indicator.normalized_frequency:
        return []
    
    if end_date is None:
        end_date = date.today()
    
    frequency = indicator.normalized_frequency
    expected_periods = _get_expected_periods(indicator, frequency, end_date)
    actual_periods = _get_actual_evidence_periods(indicator)
    
    missing = _find_missing_periods(expected_periods, actual_periods)
    
    return missing


def update_evidence_period_compliance(indicator: Indicator) -> None:
    """
    Update EvidencePeriod records for an indicator and recalculate compliance.
    
    Args:
        indicator: Indicator instance
    """
    if indicator.schedule_type != 'recurring' or not indicator.normalized_frequency:
        return
    
    today = date.today()
    frequency = indicator.normalized_frequency
    
    # Get all expected periods
    expected_periods = _get_expected_periods(indicator, frequency, today)
    
    # Update or create EvidencePeriod records
    for period_start, period_end in expected_periods:
        evidence_period, created = EvidencePeriod.objects.get_or_create(
            indicator=indicator,
            period_start=period_start,
            period_end=period_end,
            defaults={'expected_evidence_count': 1}
        )
        
        # Count actual evidence for this period
        actual_count = Evidence.objects.filter(
            indicator=indicator,
            period_start__lte=period_end,
            period_end__gte=period_start
        ).count()
        
        # Update actual count and compliance status
        evidence_period.actual_evidence_count = actual_count
        evidence_period.is_compliant = actual_count >= evidence_period.expected_evidence_count
        evidence_period.save()


def _get_expected_periods(indicator: Indicator, frequency: str, end_date: date) -> List[Tuple[date, date]]:
    """
    Get all expected evidence periods from indicator creation to end_date.
    
    Args:
        indicator: Indicator instance
        frequency: Normalized frequency string
        end_date: End date for period calculation
        
    Returns:
        List of (period_start, period_end) tuples
    """
    periods = []
    current_date = indicator.created_at.date()
    
    while current_date <= end_date:
        period_start, period_end = get_period_dates(frequency, current_date)
        
        # Avoid duplicates
        if not periods or periods[-1] != (period_start, period_end):
            periods.append((period_start, period_end))
        
        # Move to next period
        next_start = calculate_next_due_date(frequency, period_start)
        if not next_start or next_start <= current_date:
            break
        current_date = next_start
    
    return periods


def _get_actual_evidence_periods(indicator: Indicator) -> List[Tuple[date, date]]:
    """
    Get actual evidence periods from Evidence records.
    
    Args:
        indicator: Indicator instance
        
    Returns:
        List of (period_start, period_end) tuples
    """
    evidence_with_periods = Evidence.objects.filter(
        indicator=indicator
    ).exclude(
        period_start__isnull=True,
        period_end__isnull=True
    ).values_list('period_start', 'period_end', flat=False).distinct()
    
    return [(start, end) for start, end in evidence_with_periods if start and end]


def _find_missing_periods(
    expected_periods: List[Tuple[date, date]],
    actual_periods: List[Tuple[date, date]]
) -> List[Dict[str, date]]:
    """
    Find periods that are expected but not covered by actual evidence.
    
    Args:
        expected_periods: List of expected (start, end) tuples
        actual_periods: List of actual (start, end) tuples
        
    Returns:
        List of dicts with 'start' and 'end' keys for missing periods
    """
    missing = []
    
    for exp_start, exp_end in expected_periods:
        # Check if this period is covered by any actual evidence
        is_covered = False
        for act_start, act_end in actual_periods:
            # Period is covered if actual evidence overlaps with expected period
            if not (act_end < exp_start or act_start > exp_end):
                is_covered = True
                break
        
        if not is_covered:
            missing.append({'start': exp_start, 'end': exp_end})
    
    return missing


def recalculate_indicator_compliance(indicator: Indicator) -> None:
    """
    Recalculate and update indicator compliance status based on evidence.
    
    Args:
        indicator: Indicator instance
    """
    compliance = calculate_compliance_status(indicator)
    
    # Update indicator status
    new_status = compliance['status']
    if indicator.status != new_status:
        # Create status history entry if status changed
        from .models import IndicatorStatusHistory
        IndicatorStatusHistory.objects.create(
            indicator=indicator,
            old_status=indicator.status,
            new_status=new_status,
            notes=f"Auto-updated based on evidence compliance calculation"
        )
        indicator.status = new_status
        indicator.save(update_fields=['status'])
    
    # Update evidence periods
    update_evidence_period_compliance(indicator)

