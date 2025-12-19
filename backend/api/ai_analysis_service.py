"""
AI Analysis Service for indicator frequency determination.
"""
import re
from typing import Dict, Optional
from django.conf import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def analyze_indicator_frequency(
    section: str,
    standard: str, 
    indicator_text: str,
    evidence_required: str,
    frequency_text: str
) -> Optional[Dict]:
    """
    Analyze indicator frequency using AI to determine if it's one-time or recurring.
    
    Args:
        section: Section name
        standard: Standard name
        indicator_text: Indicator requirement text
        evidence_required: Evidence description
        frequency_text: Original frequency text from CSV
        
    Returns:
        Dictionary with schedule_type, normalized_frequency, analysis_data, and confidence_score
        or None if analysis fails
    """
    # First, try rule-based detection for common patterns
    rule_based_result = _rule_based_frequency_detection(frequency_text)
    
    # If rule-based detection is confident, use it
    if rule_based_result and rule_based_result.get('confidence_score', 0) > 0.8:
        return rule_based_result
    
    # Otherwise, use AI analysis
    ai_result = _ai_frequency_analysis(
        section, standard, indicator_text, 
        evidence_required, frequency_text
    )
    
    # If AI fails, fall back to rule-based result
    if not ai_result:
        return rule_based_result or _default_frequency_result(frequency_text)
    
    return ai_result


def _rule_based_frequency_detection(frequency_text: str) -> Optional[Dict]:
    """
    Rule-based frequency detection for common patterns.
    
    Returns schedule_type and normalized_frequency based on keywords.
    """
    if not frequency_text:
        return {
            'schedule_type': 'one_time',
            'normalized_frequency': '',
            'analysis_data': {'method': 'rule_based', 'reason': 'Empty frequency'},
            'confidence_score': 0.9
        }
    
    freq_lower = frequency_text.lower().strip()
    
    # One-time patterns
    one_time_patterns = [
        'one time', 'onetime', 'once', 'one-time', 'initial', 'setup',
        'n/a', 'na', 'not applicable', 'none'
    ]
    
    for pattern in one_time_patterns:
        if pattern in freq_lower:
            return {
                'schedule_type': 'one_time',
                'normalized_frequency': '',
                'analysis_data': {
                    'method': 'rule_based',
                    'pattern_matched': pattern,
                    'original': frequency_text
                },
                'confidence_score': 0.95
            }
    
    # Recurring patterns with normalization
    recurring_patterns = {
        'Daily': ['daily', 'every day', 'each day'],
        'Weekly': ['weekly', 'every week', 'each week'],
        'Bi-weekly': ['bi-weekly', 'biweekly', 'every 2 weeks', 'every two weeks', 'fortnightly'],
        'Monthly': ['monthly', 'every month', 'each month'],
        'Quarterly': ['quarterly', 'every quarter', 'every 3 months', 'every three months'],
        'Semi-annually': ['semi-annual', 'semiannual', 'twice a year', 'every 6 months', 'every six months'],
        'Annual': ['annual', 'annually', 'yearly', 'every year', 'each year'],
    }
    
    for normalized, patterns in recurring_patterns.items():
        for pattern in patterns:
            if pattern in freq_lower:
                return {
                    'schedule_type': 'recurring',
                    'normalized_frequency': normalized,
                    'analysis_data': {
                        'method': 'rule_based',
                        'pattern_matched': pattern,
                        'original': frequency_text
                    },
                    'confidence_score': 0.95
                }
    
    # If contains numbers, likely recurring
    if re.search(r'\d+', freq_lower):
        return {
            'schedule_type': 'recurring',
            'normalized_frequency': frequency_text,  # Keep original if can't normalize
            'analysis_data': {
                'method': 'rule_based',
                'reason': 'Contains numeric value, assumed recurring',
                'original': frequency_text
            },
            'confidence_score': 0.7
        }
    
    # Default to one_time with low confidence
    return {
        'schedule_type': 'one_time',
        'normalized_frequency': '',
        'analysis_data': {
            'method': 'rule_based',
            'reason': 'No pattern matched, defaulting to one-time',
            'original': frequency_text
        },
        'confidence_score': 0.5
    }


def _ai_frequency_analysis(
    section: str,
    standard: str,
    indicator_text: str,
    evidence_required: str,
    frequency_text: str
) -> Optional[Dict]:
    """
    Use AI to analyze indicator frequency.
    
    Returns dictionary with analysis results or None if AI unavailable/fails.
    """
    if not GEMINI_AVAILABLE:
        return None
    
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
Analyze the following compliance indicator and determine if it's a ONE-TIME or RECURRING requirement.

Section: {section}
Standard: {standard}
Indicator: {indicator_text}
Evidence Required: {evidence_required}
Frequency Text: {frequency_text}

Respond with a JSON object in this exact format:
{{
    "schedule_type": "one_time" or "recurring",
    "normalized_frequency": "Daily" or "Weekly" or "Monthly" or "Quarterly" or "Annual" or "" (if one-time),
    "reasoning": "Brief explanation of your decision",
    "confidence_score": 0.0 to 1.0
}}

Rules:
- If frequency text is empty or says "one time", "once", "initial", it's one_time
- If frequency mentions "daily", "weekly", "monthly", "quarterly", "annual", it's recurring
- If evidence suggests ongoing monitoring or periodic review, it's likely recurring
- Normalize frequency to one of: Daily, Weekly, Bi-weekly, Monthly, Quarterly, Semi-annually, Annual
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON response
        import json
        
        # Extract JSON from markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        data = json.loads(response_text)
        
        return {
            'schedule_type': data.get('schedule_type', 'one_time'),
            'normalized_frequency': data.get('normalized_frequency', ''),
            'analysis_data': {
                'method': 'ai',
                'reasoning': data.get('reasoning', ''),
                'original': frequency_text,
                'raw_response': response_text
            },
            'confidence_score': float(data.get('confidence_score', 0.5))
        }
        
    except Exception as e:
        # AI failed, return None to fall back to rule-based
        return None


def _default_frequency_result(frequency_text: str) -> Dict:
    """Return a default result when all analysis fails."""
    return {
        'schedule_type': 'one_time',
        'normalized_frequency': '',
        'analysis_data': {
            'method': 'default',
            'reason': 'All analysis methods failed',
            'original': frequency_text
        },
        'confidence_score': 0.3
    }
