"""
AI Evidence Service for indicator-aware AI assistance.

Provides contextual help for evidence collection, SOP generation, form suggestions,
and compliance gap explanations.
"""
from typing import Dict, Optional, List
from django.conf import settings
from .models import Indicator, Evidence

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def analyze_indicator_evidence_requirements(indicator: Indicator) -> Dict[str, any]:
    """
    Analyze indicator and suggest appropriate evidence types and requirements.
    
    Args:
        indicator: Indicator instance
        
    Returns:
        Dict with evidence suggestions and recommendations
    """
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return {
            'error': 'AI service not available',
            'suggestions': _get_default_evidence_suggestions(indicator)
        }
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
As a compliance expert for medical institutions, laboratories, and universities, analyze this compliance indicator and provide evidence recommendations.

Indicator Details:
- Section: {indicator.section.name if indicator.section else indicator.area or 'N/A'}
- Standard: {indicator.standard.name if indicator.standard else indicator.regulation_or_standard or 'N/A'}
- Requirement: {indicator.requirement}
- Evidence Required (as stated): {indicator.evidence_required or 'Not specified'}
- Frequency: {indicator.normalized_frequency or indicator.frequency or 'One-time'}
- Schedule Type: {indicator.schedule_type}

Provide a JSON response with:
{{
    "recommended_evidence_mode": "file_only" | "text_only" | "hybrid" | "frequency_log",
    "acceptable_evidence_types": ["list", "of", "specific", "evidence", "types"],
    "examples": ["example 1", "example 2"],
    "reasoning": "explanation of why these evidence types are appropriate",
    "compliance_notes": "additional guidance for meeting this requirement"
}}
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON from response
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Try to extract JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(response_text)
        
        return {
            'suggestions': data,
            'confidence': 0.85
        }
    except Exception as e:
        return {
            'error': f'AI analysis failed: {str(e)}',
            'suggestions': _get_default_evidence_suggestions(indicator)
        }


def generate_evidence_suggestions(indicator: Indicator) -> List[Dict[str, str]]:
    """
    Generate specific evidence suggestions for an indicator.
    
    Args:
        indicator: Indicator instance
        
    Returns:
        List of evidence suggestion dicts
    """
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return _get_default_evidence_suggestions(indicator).get('examples', [])
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
For this compliance indicator, suggest 5-7 specific, actionable evidence items that would satisfy the requirement.

Indicator: {indicator.requirement}
Evidence Required: {indicator.evidence_required or 'Not specified'}
Frequency: {indicator.normalized_frequency or indicator.frequency or 'One-time'}

Provide a JSON array of evidence suggestions:
[
    {{
        "title": "Evidence item title",
        "type": "file" | "text" | "hybrid",
        "description": "What this evidence should contain",
        "priority": "high" | "medium" | "low"
    }}
]
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        import json
        import re
        
        # Extract JSON array
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group())
        else:
            suggestions = json.loads(response_text)
        
        return suggestions
    except Exception as e:
        return _get_default_evidence_suggestions(indicator).get('examples', [])


def draft_sop_or_policy(indicator: Indicator, document_type: str = 'SOP') -> Dict[str, str]:
    """
    Draft an SOP or policy document for an indicator.
    
    Args:
        indicator: Indicator instance
        document_type: 'SOP' or 'Policy'
        
    Returns:
        Dict with document content and metadata
    """
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return {
            'error': 'AI service not available',
            'document': _get_default_sop_template(indicator, document_type)
        }
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
Draft a comprehensive {document_type} (Standard Operating Procedure) document for this compliance requirement.

Indicator: {indicator.requirement}
Evidence Required: {indicator.evidence_required or 'Not specified'}
Responsible Person: {indicator.responsible_person or 'To be assigned'}
Frequency: {indicator.normalized_frequency or indicator.frequency or 'One-time'}

The {document_type} should include:
1. Purpose and scope
2. Definitions
3. Procedures/steps
4. Responsibilities
5. Documentation requirements
6. Review and approval process
7. References

Format as a professional document ready for use in a medical institution or laboratory.
"""
        
        response = model.generate_content(prompt)
        document_content = response.text.strip()
        
        return {
            'document_type': document_type,
            'title': f"{document_type} for {indicator.requirement[:50]}",
            'content': document_content,
            'indicator_id': indicator.id,
            'suggested_filename': f"{document_type}_{indicator.id}_{indicator.requirement[:30].replace(' ', '_')}.docx"
        }
    except Exception as e:
        return {
            'error': f'Document generation failed: {str(e)}',
            'document': _get_default_sop_template(indicator, document_type)
        }


def suggest_digital_form(indicator: Indicator) -> Dict[str, any]:
    """
    Suggest a digital form template for recurring indicators.
    
    Args:
        indicator: Indicator instance
        
    Returns:
        Dict with form field suggestions
    """
    if indicator.schedule_type != 'recurring':
        return {
            'error': 'Form suggestions are only for recurring indicators',
            'suggestion': None
        }
    
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return {
            'suggestion': _get_default_form_fields(indicator)
        }
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
Design a digital form template for collecting recurring compliance evidence for this indicator.

Indicator: {indicator.requirement}
Evidence Required: {indicator.evidence_required or 'Not specified'}
Frequency: {indicator.normalized_frequency or indicator.frequency}

Provide a JSON object with form field definitions:
{{
    "form_name": "Suggested form name",
    "form_description": "Purpose of this form",
    "fields": [
        {{
            "name": "field_name",
            "label": "Field Label",
            "type": "text" | "date" | "number" | "select" | "checkbox" | "textarea",
            "required": true | false,
            "options": ["option1", "option2"]  // if type is select
        }}
    ],
    "frequency": "{indicator.normalized_frequency or indicator.frequency}"
}}
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        import json
        import re
        
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            suggestion = json.loads(json_match.group())
        else:
            suggestion = json.loads(response_text)
        
        return {
            'suggestion': suggestion,
            'indicator_id': indicator.id
        }
    except Exception as e:
        return {
            'error': f'Form suggestion failed: {str(e)}',
            'suggestion': _get_default_form_fields(indicator)
        }


def explain_compliance_gaps(indicator: Indicator) -> Dict[str, any]:
    """
    Explain why compliance is incomplete and what's missing.
    
    Args:
        indicator: Indicator instance
        
    Returns:
        Dict with gap analysis and recommendations
    """
    from .compliance_service import calculate_compliance_status, get_missing_periods
    
    compliance_status = calculate_compliance_status(indicator)
    missing_periods = get_missing_periods(indicator)
    existing_evidence = indicator.evidence.all()
    
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return {
            'status': compliance_status['status'],
            'missing_periods': missing_periods,
            'explanation': _get_default_gap_explanation(indicator, compliance_status, missing_periods)
        }
    
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        evidence_summary = []
        for ev in existing_evidence[:5]:  # Limit to recent evidence
            evidence_summary.append(f"- {ev.title} ({ev.evidence_type}) - {ev.uploaded_at.date()}")
        
        prompt = f"""
Analyze this compliance indicator's current status and explain what's missing for full compliance.

Indicator: {indicator.requirement}
Current Status: {compliance_status['status']}
Evidence Count: {compliance_status['evidence_count']} / {compliance_status.get('expected_count', 'N/A')}
Frequency: {indicator.normalized_frequency or indicator.frequency or 'One-time'}

Existing Evidence:
{chr(10).join(evidence_summary) if evidence_summary else 'None'}

Missing Periods: {len(missing_periods)}

Provide a clear explanation:
1. Why compliance is incomplete
2. What specific evidence is missing
3. Recommended actions to achieve compliance
4. Priority of actions

Format as a helpful, actionable explanation.
"""
        
        response = model.generate_content(prompt)
        explanation = response.text.strip()
        
        return {
            'status': compliance_status['status'],
            'missing_periods': missing_periods,
            'explanation': explanation,
            'recommendations': _extract_recommendations(explanation)
        }
    except Exception as e:
        return {
            'status': compliance_status['status'],
            'missing_periods': missing_periods,
            'explanation': _get_default_gap_explanation(indicator, compliance_status, missing_periods),
            'error': f'AI explanation failed: {str(e)}'
        }


def _get_default_evidence_suggestions(indicator: Indicator) -> Dict:
    """Fallback evidence suggestions when AI is unavailable."""
    return {
        'recommended_evidence_mode': indicator.evidence_mode or 'hybrid',
        'acceptable_evidence_types': ['Document', 'Record', 'Certificate', 'Report'],
        'examples': [
            {'title': 'Compliance document', 'type': 'file', 'description': 'Primary evidence document'},
            {'title': 'Physical evidence declaration', 'type': 'text', 'description': 'If evidence is physical'}
        ],
        'reasoning': 'Based on indicator requirements',
        'compliance_notes': indicator.evidence_required or 'Follow standard compliance practices'
    }


def _get_default_sop_template(indicator: Indicator, doc_type: str) -> str:
    """Fallback SOP template."""
    return f"""
{doc_type} for: {indicator.requirement}

Purpose:
This {doc_type.lower()} establishes procedures for compliance with: {indicator.requirement}

Scope:
Applies to: {indicator.responsible_person or 'All relevant personnel'}

Procedures:
1. Review requirement: {indicator.requirement}
2. Collect evidence: {indicator.evidence_required or 'As specified'}
3. Document compliance
4. Review and approve

Responsibilities:
- Responsible Person: {indicator.responsible_person or 'To be assigned'}

Review Frequency: {indicator.normalized_frequency or indicator.frequency or 'As needed'}
"""


def _get_default_form_fields(indicator: Indicator) -> Dict:
    """Fallback form fields."""
    return {
        'form_name': f'Compliance Form - {indicator.requirement[:30]}',
        'form_description': f'Form for collecting evidence for: {indicator.requirement}',
        'fields': [
            {'name': 'date', 'label': 'Date', 'type': 'date', 'required': True},
            {'name': 'notes', 'label': 'Notes', 'type': 'textarea', 'required': False},
            {'name': 'submitted_by', 'label': 'Submitted By', 'type': 'text', 'required': True}
        ],
        'frequency': indicator.normalized_frequency or indicator.frequency
    }


def _get_default_gap_explanation(indicator: Indicator, status: Dict, missing: List) -> str:
    """Fallback gap explanation."""
    if status['status'] == 'compliant':
        return "Compliance is complete. All required evidence has been submitted."
    
    if missing:
        return f"Missing evidence for {len(missing)} period(s). Please submit evidence for the missing periods to achieve compliance."
    
    return f"Evidence is incomplete. Current status: {status['status']}. Please review the indicator requirements and submit appropriate evidence."


def _extract_recommendations(explanation: str) -> List[str]:
    """Extract action items from explanation text."""
    recommendations = []
    lines = explanation.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ['recommend', 'should', 'must', 'need', 'action']):
            recommendations.append(line.strip())
    return recommendations[:5]  # Limit to 5 recommendations

