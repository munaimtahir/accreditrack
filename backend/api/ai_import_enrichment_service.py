"""
AI Import Enrichment Service for automatically enriching indicators during CSV import.

This service provides:
- AI-generated summaries and implementation plans
- Evidence examples
- Frequency/logging classification
- AI help level assessment
- Digital form template generation for recurring indicators
"""
import json
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import Indicator, DigitalFormTemplate
from .ai_analysis_service import analyze_indicator_frequency

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None  # type: ignore


def enrich_indicators_for_import(
    indicators: List[Indicator],
    user=None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Enrich a list of indicators with AI-generated content.
    
    Args:
        indicators: List of Indicator instances to enrich
        user: Optional user who triggered the enrichment
        force: If True, re-enrich even if enrichment data exists
        
    Returns:
        Dict with enrichment statistics and any errors
    """
    if not indicators:
        return {
            'enriched_count': 0,
            'skipped_count': 0,
            'errors': [],
            'gemini_calls': 0
        }
    
    # Filter indicators that need enrichment
    to_enrich = []
    skipped = 0
    
    for indicator in indicators:
        if not force and _has_enrichment_data(indicator):
            skipped += 1
            continue
        to_enrich.append(indicator)
    
    if not to_enrich:
        return {
            'enriched_count': 0,
            'skipped_count': skipped,
            'errors': [],
            'gemini_calls': 0
        }
    
    # Process in batches of 10-25 indicators
    batch_size = 20  # Safe middle ground
    total_batches = (len(to_enrich) + batch_size - 1) // batch_size
    gemini_calls = 0
    errors = []
    enriched_count = 0
    
    for batch_idx in range(total_batches):
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, len(to_enrich))
        batch = to_enrich[batch_start:batch_end]
        
        try:
            # Try AI enrichment first
            batch_results = _enrich_batch_with_ai(batch)
            gemini_calls += 1
            
            if batch_results:
                # Successfully enriched with AI
                for indicator, enrichment_data in zip(batch, batch_results):
                    try:
                        _save_enrichment_data(indicator, enrichment_data)
                        _apply_enrichment_to_indicator(indicator, enrichment_data, user)
                        enriched_count += 1
                    except Exception as e:
                        logger.error(f"Failed to save enrichment for indicator {indicator.id}: {e}")
                        errors.append({
                            'indicator_id': indicator.id,
                            'error': str(e)
                        })
            else:
                # AI failed, use rule-based fallback
                logger.warning(f"AI enrichment failed for batch {batch_idx + 1}, using rule-based fallback")
                for indicator in batch:
                    try:
                        enrichment_data = _rule_based_enrichment(indicator)
                        _save_enrichment_data(indicator, enrichment_data)
                        _apply_enrichment_to_indicator(indicator, enrichment_data, user)
                        enriched_count += 1
                    except Exception as e:
                        logger.error(f"Failed rule-based enrichment for indicator {indicator.id}: {e}")
                        errors.append({
                            'indicator_id': indicator.id,
                            'error': str(e)
                        })
                        
        except Exception as e:
            logger.error(f"Failed to process batch {batch_idx + 1}: {e}")
            # Fallback to rule-based for this batch
            for indicator in batch:
                try:
                    enrichment_data = _rule_based_enrichment(indicator)
                    _save_enrichment_data(indicator, enrichment_data)
                    _apply_enrichment_to_indicator(indicator, enrichment_data, user)
                    enriched_count += 1
                except Exception as e2:
                    logger.error(f"Failed rule-based enrichment for indicator {indicator.id}: {e2}")
                    errors.append({
                        'indicator_id': indicator.id,
                        'error': str(e2)
                    })
    
    return {
        'enriched_count': enriched_count,
        'skipped_count': skipped,
        'errors': errors,
        'gemini_calls': gemini_calls
    }


def _enrich_batch_with_ai(indicators: List[Indicator]) -> Optional[List[Dict[str, Any]]]:
    """
    Enrich a batch of indicators using Gemini AI.
    
    Returns:
        List of enrichment data dicts, one per indicator, or None if AI unavailable/fails
    """
    if not GEMINI_AVAILABLE or genai is None:
        return None
    
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build prompt with all indicators in batch
        prompt = _build_batch_enrichment_prompt(indicators)
        
        # Generate with strict JSON output requirement
        generation_config = {
            'temperature': 0.3,  # Lower temperature for more consistent output
            'max_output_tokens': 8000,  # Limit output size
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        response_text = response.text.strip()
        
        # Parse JSON from response
        parsed_data = _parse_json_response(response_text)
        
        if not parsed_data or not isinstance(parsed_data, list):
            logger.error(f"Failed to parse batch enrichment response: invalid format")
            return None
        
        # Ensure we have the right number of results
        if len(parsed_data) != len(indicators):
            logger.warning(f"Received {len(parsed_data)} enrichment results for {len(indicators)} indicators")
            # Try to fix by retrying with stricter prompt
            return _retry_batch_with_repair_prompt(indicators, response_text)
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Gemini API error during batch enrichment: {e}")
        return None


def _build_batch_enrichment_prompt(indicators: List[Indicator]) -> str:
    """Build a prompt for batch enrichment of indicators."""
    indicators_data = []
    
    for idx, indicator in enumerate(indicators):
        section_name = indicator.section.name if indicator.section else indicator.area or 'N/A'
        standard_name = indicator.standard.name if indicator.standard else indicator.regulation_or_standard or 'N/A'
        
        indicators_data.append({
            'id': idx + 1,
            'section': section_name,
            'standard': standard_name,
            'requirement': indicator.requirement,
            'evidence_required': indicator.evidence_required or 'Not specified',
            'frequency': indicator.frequency or 'Not specified',
            'normalized_frequency': indicator.normalized_frequency or '',
            'schedule_type': indicator.schedule_type
        })
    
    prompt = f"""You are a compliance expert for medical institutions, laboratories, and universities.

Analyze the following {len(indicators)} compliance indicators and provide structured enrichment data for each.

Return ONLY a JSON array. No markdown. No explanation. No code blocks. Just the JSON array.

Each indicator must have this exact structure:
{{
    "ai_summary": "1-2 line summary",
    "ai_implementation_steps": ["step 1", "step 2", "step 3", "step 4", "step 5"],
    "ai_evidence_examples": ["example 1", "example 2", "example 3"],
    "indicator_type": "one_time" | "periodic_logging" | "continuous_practice" | "event_triggered",
    "frequency_detected": "normalized frequency string or empty",
    "logging_plan": {{
        "log_name": "name for the log",
        "log_frequency": "Daily/Weekly/Monthly/etc or null",
        "min_entries_per_period": number or null,
        "who_fills": "role description or null",
        "who_verifies": "role description or null",
        "fields": [
            {{
                "name": "field_name",
                "label": "Field Label",
                "type": "text" | "date" | "number" | "select" | "checkbox" | "textarea",
                "required": true | false,
                "options": ["option1", "option2"]  // only if type is "select"
            }}
        ]
    }} OR null,
    "ai_help_level": "high" | "medium" | "low",
    "ai_help_reason": "brief explanation"
}}

RULES:
- indicator_type: Use "periodic_logging" if frequency suggests recurring entries (daily/weekly/monthly logs)
- indicator_type: Use "continuous_practice" if it's an ongoing practice/policy
- indicator_type: Use "event_triggered" if it happens on specific events
- indicator_type: Use "one_time" if it's a one-time setup/initial documentation
- If indicator_type is "periodic_logging" and normalized_frequency exists, include logging_plan with fields
- ai_implementation_steps: 5-8 actionable steps
- ai_evidence_examples: 3-6 specific examples
- ai_help_level: "high" if AI can generate templates/forms/documents, "medium" if AI can guide, "low" if physical action required
- logging_plan.fields: Only include if indicator_type is "periodic_logging" and frequency suggests regular logging

INDICATORS:
{json.dumps(indicators_data, indent=2)}

Return the JSON array now (one object per indicator, in order):"""
    
    return prompt


def _parse_json_response(response_text: str) -> Optional[List[Dict[str, Any]]]:
    """Parse JSON from Gemini response, handling markdown code blocks."""
    try:
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            # Try to extract JSON from any code block
            parts = response_text.split('```')
            if len(parts) >= 2:
                response_text = parts[1].strip()
                # Remove language identifier if present
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
        
        # Try to extract JSON array from text
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()
        
        # Parse JSON
        data = json.loads(response_text)
        return data if isinstance(data, list) else None
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}, response_text preview: {response_text[:200]}")
        return None


def _retry_batch_with_repair_prompt(
    indicators: List[Indicator],
    original_response: str
) -> Optional[List[Dict[str, Any]]]:
    """
    Retry parsing with a repair prompt if initial parsing fails.
    """
    if not GEMINI_AVAILABLE or not settings.GEMINI_API_KEY:
        return None
    
    try:
        if not GEMINI_AVAILABLE or genai is None:
            return None
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""The previous response had JSON parsing errors. Please extract and return ONLY the JSON array, one object per indicator.

Original response (may have formatting issues):
{original_response[:2000]}

Required: Return ONLY the valid JSON array with {len(indicators)} objects. No markdown. No explanation."""
        
        response = model.generate_content(prompt)
        return _parse_json_response(response.text.strip())
        
    except Exception as e:
        logger.error(f"Retry repair failed: {e}")
        return None


def _rule_based_enrichment(indicator: Indicator) -> Dict[str, Any]:
    """
    Generate enrichment data using rule-based logic (fallback when AI unavailable).
    """
    # Convert model fields to strings
    section_name = str(indicator.section.name) if indicator.section else str(indicator.area) if indicator.area else ''
    standard_name = str(indicator.standard.name) if indicator.standard else str(indicator.regulation_or_standard) if indicator.regulation_or_standard else ''
    requirement_text = str(indicator.requirement)
    evidence_text = str(indicator.evidence_required) if indicator.evidence_required else ''
    frequency_text = str(indicator.frequency) if indicator.frequency else ''
    normalized_freq = str(indicator.normalized_frequency) if indicator.normalized_frequency else ''
    schedule_type = str(indicator.schedule_type)
    
    # Use existing frequency analysis
    freq_analysis = analyze_indicator_frequency(
        section_name,
        standard_name,
        requirement_text,
        evidence_text,
        frequency_text
    )
    
    # Determine indicator type
    if schedule_type == 'recurring' and normalized_freq:
        indicator_type = 'periodic_logging'
    elif 'policy' in requirement_text.lower() or 'procedure' in requirement_text.lower():
        indicator_type = 'continuous_practice'
    elif 'initial' in requirement_text.lower() or 'setup' in requirement_text.lower():
        indicator_type = 'one_time'
    else:
        indicator_type = 'one_time'
    
    # Generate basic implementation steps
    implementation_steps = [
        "Review the requirement and understand compliance objectives",
        "Identify responsible personnel and assign roles",
        "Gather necessary documentation and evidence",
        "Implement required processes or procedures",
        "Document compliance and maintain records",
        "Schedule regular reviews and updates"
    ]
    
    # Generate evidence examples from evidence_required
    evidence_examples = []
    if evidence_text:
        # Try to extract examples from evidence_required text
        if ';' in evidence_text:
            examples = [e.strip() for e in evidence_text.split(';')[:6]]
            evidence_examples = examples
        elif ',' in evidence_text:
            examples = [e.strip() for e in evidence_text.split(',')[:6]]
            evidence_examples = examples
        else:
            evidence_examples = [evidence_text]
    
    # Add default examples if needed
    if not evidence_examples:
        evidence_examples = [
            "Compliance documentation",
            "Supporting records",
            "Verification certificates"
        ]
    
    # Determine AI help level
    ai_help_level = 'medium'
    ai_help_reason = "AI can provide guidance and structure"
    
    # Check for physical keywords
    physical_keywords = ['inspection', 'maintenance', 'repair', 'calibration', 'physical', 'equipment']
    if any(keyword in requirement_text.lower() for keyword in physical_keywords):
        ai_help_level = 'low'
        ai_help_reason = "Requires physical action or real-world inspection"
    elif 'document' in requirement_text.lower() or 'policy' in requirement_text.lower():
        ai_help_level = 'high'
        ai_help_reason = "AI can generate draft documents and templates"
    
    # Build logging plan if periodic
    logging_plan = None
    if indicator_type == 'periodic_logging' and normalized_freq:
        requirement_short = requirement_text[:40] if len(requirement_text) > 40 else requirement_text
        logging_plan = {
            'log_name': f"Log - {requirement_short}",
            'log_frequency': normalized_freq,
            'min_entries_per_period': _get_min_entries_for_frequency(normalized_freq),
            'who_fills': str(indicator.responsible_person) if indicator.responsible_person else 'Assigned personnel',
            'who_verifies': 'Supervisor',
            'fields': [
                {'name': 'date', 'label': 'Date', 'type': 'date', 'required': True},
                {'name': 'notes', 'label': 'Notes', 'type': 'textarea', 'required': False},
                {'name': 'submitted_by', 'label': 'Submitted By', 'type': 'text', 'required': True}
            ]
        }
    
    summary = requirement_text[:150] + ('...' if len(requirement_text) > 150 else '')
    
    return {
        'ai_summary': summary,
        'ai_implementation_steps': implementation_steps,
        'ai_evidence_examples': evidence_examples[:6],
        'indicator_type': indicator_type,
        'frequency_detected': normalized_freq,
        'logging_plan': logging_plan,
        'ai_help_level': ai_help_level,
        'ai_help_reason': ai_help_reason,
        'created_by_ai_at': timezone.now().isoformat(),
        'model': 'rule_based'
    }


def _get_min_entries_for_frequency(frequency: str) -> int:
    """Get minimum entries per period based on frequency."""
    freq_lower = frequency.lower().strip()
    if freq_lower in ['daily', 'day']:
        return 1
    elif freq_lower in ['weekly', 'week']:
        return 1
    elif freq_lower in ['bi-weekly', 'biweekly', 'fortnightly']:
        return 1
    elif freq_lower in ['monthly', 'month']:
        return 1
    elif freq_lower in ['quarterly', 'quarter']:
        return 1
    elif freq_lower in ['semi-annually', 'semiannually']:
        return 1
    elif freq_lower in ['annual', 'annually', 'yearly']:
        return 1
    return 1


def _save_enrichment_data(indicator: Indicator, enrichment_data: Dict[str, Any]):
    """Save enrichment data to indicator's ai_analysis_data field."""
    # Get existing data or create new dict
    existing_data = indicator.ai_analysis_data if indicator.ai_analysis_data else {}
    if not isinstance(existing_data, dict):
        existing_data = {}
    
    # Update with enrichment data
    existing_data['import_enrichment'] = enrichment_data
    # JSONField accepts dict directly
    indicator.ai_analysis_data = existing_data  # type: ignore
    indicator.save(update_fields=['ai_analysis_data'])


def _apply_enrichment_to_indicator(
    indicator: Indicator,
    enrichment_data: Dict[str, Any],
    user=None
):
    """
    Apply enrichment data to indicator, including:
    - Setting evidence_mode if periodic_logging
    - Creating DigitalFormTemplate if logging_plan exists
    - Updating schedule_type and next_due_date if needed
    """
    # Update indicator_type classification
    indicator_type = enrichment_data.get('indicator_type')
    
    # If periodic_logging, set evidence_mode
    if indicator_type == 'periodic_logging':
        updates = {}
        
        if str(indicator.evidence_mode) != 'frequency_log':
            updates['evidence_mode'] = 'frequency_log'
        
        # Ensure schedule_type is recurring
        if str(indicator.schedule_type) != 'recurring':
            updates['schedule_type'] = 'recurring'
            from .scheduling_service import calculate_next_due_date
            normalized_freq = str(indicator.normalized_frequency) if indicator.normalized_frequency else None
            if normalized_freq:
                next_due = calculate_next_due_date(normalized_freq)
                if next_due:
                    updates['next_due_date'] = next_due
        
        if updates:
            for field, value in updates.items():
                setattr(indicator, field, value)
            indicator.save(update_fields=list(updates.keys()))
    
    # Create DigitalFormTemplate if logging_plan exists
    logging_plan = enrichment_data.get('logging_plan')
    if logging_plan and logging_plan.get('fields'):
        # Check if template already exists
        existing_template = DigitalFormTemplate.objects.filter(indicator=indicator).first()
        
        if not existing_template:
            # Create new template
            indicator_code = str(indicator.indicator_code) if indicator.indicator_code else ''
            requirement_text = str(indicator.requirement)
            requirement_short = requirement_text[:40] if len(requirement_text) > 40 else requirement_text
            
            form_name = logging_plan.get('log_name', f"Log template - {indicator_code or requirement_short}")
            description = enrichment_data.get('ai_summary', requirement_text)
            
            DigitalFormTemplate.objects.create(
                indicator=indicator,
                name=form_name,
                description=description,
                form_fields=logging_plan['fields'],
                created_by=user
            )
            logger.info(f"Created DigitalFormTemplate for indicator {indicator.id}")


def _has_enrichment_data(indicator: Indicator) -> bool:
    """Check if indicator already has import enrichment data."""
    if not indicator.ai_analysis_data:
        return False
    if not isinstance(indicator.ai_analysis_data, dict):
        return False
    return 'import_enrichment' in indicator.ai_analysis_data

