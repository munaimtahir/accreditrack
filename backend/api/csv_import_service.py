"""
CSV Import Service for bulk indicator imports.
"""
import csv
import io
from typing import Dict, List, Any
from django.db import transaction
from django.contrib.auth.models import User
from .models import Project, Section, Standard, Indicator
from .ai_analysis_service import analyze_indicator_frequency


class CSVImportResult:
    """Container for import results."""
    
    def __init__(self):
        self.sections_created = 0
        self.standards_created = 0
        self.indicators_created = 0
        self.indicators_updated = 0
        self.rows_skipped = 0
        self.errors = []
        self.unmatched_users = []
        self.indicators_processed = []  # Track indicator IDs for enrichment
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            'sections_created': self.sections_created,
            'standards_created': self.standards_created,
            'indicators_created': self.indicators_created,
            'indicators_updated': self.indicators_updated,
            'rows_skipped': self.rows_skipped,
            'total_rows_processed': self.indicators_created + self.indicators_updated + self.rows_skipped,
            'errors': self.errors,
            'unmatched_users': list(set(self.unmatched_users)),
        }


class CSVImportService:
    """Service for importing indicators from CSV files."""
    
    REQUIRED_HEADERS = [
        'Section',
        'Standard',
        'Indicator',
        'Evidence Required',
        'Responsible Person',
        'Frequency',
        'Assigned to',
        'Compliance Evidence',
        'Score'
    ]
    
    def __init__(self, project: Project):
        self.project = project
        self.result = CSVImportResult()
        self.section_cache = {}  # Cache sections to avoid repeated DB lookups
        self.standard_cache = {}  # Cache standards
    
    def import_csv(self, csv_file, run_ai_enrichment: bool = True, user=None) -> CSVImportResult:
        """
        Import indicators from CSV file.
        
        Args:
            csv_file: File object containing CSV data
            run_ai_enrichment: Whether to run AI enrichment after import (default: True)
            user: Optional user who triggered the import (for enrichment tracking)
            
        Returns:
            CSVImportResult with import summary
        """
        try:
            # Read and decode CSV file
            csv_content = csv_file.read()
            if isinstance(csv_content, bytes):
                csv_content = csv_content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Validate headers
            if not self._validate_headers(csv_reader.fieldnames):
                self.result.errors.append({
                    'row': 0,
                    'error': f'Invalid CSV headers. Expected: {", ".join(self.REQUIRED_HEADERS)}'
                })
                return self.result
            
            # Process rows in a single transaction
            with transaction.atomic():
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (1 is header)
                    try:
                        indicator = self._process_row(row, row_num)
                        if indicator:
                            self.result.indicators_processed.append(indicator)
                    except Exception as e:
                        self.result.rows_skipped += 1
                        self.result.errors.append({
                            'row': row_num,
                            'error': str(e)
                        })
            
            # Run AI enrichment if requested
            if run_ai_enrichment and self.result.indicators_processed:
                try:
                    from .ai_import_enrichment_service import enrich_indicators_for_import
                    enrichment_result = enrich_indicators_for_import(
                        self.result.indicators_processed,
                        user=user,
                        force=False
                    )
                    # Store enrichment stats in result (for logging/debugging)
                    self.result.enrichment_stats = enrichment_result
                except Exception as e:
                    # Don't fail import if enrichment fails
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"AI enrichment failed during CSV import: {e}")
                    self.result.errors.append({
                        'row': 0,
                        'error': f'AI enrichment failed: {str(e)}'
                    })
            
            return self.result
            
        except Exception as e:
            self.result.errors.append({
                'row': 0,
                'error': f'Failed to process CSV file: {str(e)}'
            })
            return self.result
    
    def _validate_headers(self, headers: List[str]) -> bool:
        """Validate that CSV has required headers in correct order."""
        if not headers:
            return False
        
        # Check if all required headers are present
        for required in self.REQUIRED_HEADERS:
            if required not in headers:
                return False
        
        return True
    
    def _process_row(self, row: Dict[str, str], row_num: int) -> Indicator:
        """Process a single CSV row. Returns the Indicator instance."""
        # Extract and validate required fields
        section_name = row.get('Section', '').strip()
        standard_name = row.get('Standard', '').strip()
        indicator_text = row.get('Indicator', '').strip()
        
        # Skip rows with empty required fields
        if not section_name or not standard_name or not indicator_text:
            raise ValueError('Section, Standard, and Indicator are required fields')
        
        # Get or create Section (case-insensitive)
        section = self._get_or_create_section(section_name)
        
        # Get or create Standard (case-insensitive)
        standard = self._get_or_create_standard(section, standard_name)
        
        # Extract other fields
        evidence_required = row.get('Evidence Required', '').strip()
        responsible_person = row.get('Responsible Person', '').strip()
        frequency = row.get('Frequency', '').strip()
        assigned_to = row.get('Assigned to', '').strip()
        compliance_notes = row.get('Compliance Evidence', '').strip()
        
        # Parse score (default to 10)
        score_str = row.get('Score', '').strip()
        try:
            score = int(score_str) if score_str else 10
        except ValueError:
            score = 10
        
        # Generate indicator key for idempotency
        indicator_key = Indicator.generate_indicator_key_static(
            self.project.id, section_name, standard_name, indicator_text
        )
        
        # Check if indicator exists
        try:
            indicator = Indicator.objects.get(indicator_key=indicator_key)
            is_new = False
        except Indicator.DoesNotExist:
            indicator = Indicator(
                project=self.project,
                indicator_key=indicator_key
            )
            is_new = True
        
        # Update indicator fields
        indicator.section = section
        indicator.standard = standard
        indicator.requirement = indicator_text
        indicator.evidence_required = evidence_required
        indicator.responsible_person = responsible_person
        indicator.frequency = frequency
        indicator.assigned_to = assigned_to
        indicator.compliance_notes = compliance_notes
        indicator.score = score
        
        # Also populate legacy fields for backwards compatibility
        indicator.area = section_name
        indicator.regulation_or_standard = standard_name
        
        # Try to match assigned user
        if assigned_to:
            user = self._match_user(assigned_to)
            if user:
                indicator.assigned_user = user
            else:
                self.result.unmatched_users.append(assigned_to)
        
        # Analyze frequency using AI
        if frequency:
            ai_result = analyze_indicator_frequency(
                section_name, standard_name, indicator_text, 
                evidence_required, frequency
            )
            
            if ai_result:
                indicator.schedule_type = ai_result.get('schedule_type', 'one_time')
                indicator.normalized_frequency = ai_result.get('normalized_frequency', '')
                indicator.ai_analysis_data = ai_result.get('analysis_data')
                indicator.ai_confidence_score = ai_result.get('confidence_score')
                
                # Calculate next due date if recurring
                if indicator.schedule_type == 'recurring' and indicator.normalized_frequency:
                    from .scheduling_service import calculate_next_due_date
                    indicator.next_due_date = calculate_next_due_date(indicator.normalized_frequency)
        
        # Save indicator
        indicator.save()
        
        if is_new:
            self.result.indicators_created += 1
        else:
            self.result.indicators_updated += 1
        
        return indicator
    
    def _get_or_create_section(self, section_name: str) -> Section:
        """Get or create section (case-insensitive)."""
        # Check cache first
        cache_key = section_name.lower()
        if cache_key in self.section_cache:
            return self.section_cache[cache_key]
        
        # Try to find existing section (case-insensitive)
        section = Section.objects.filter(
            project=self.project,
            name__iexact=section_name
        ).first()
        
        if not section:
            section = Section.objects.create(
                project=self.project,
                name=section_name
            )
            self.result.sections_created += 1
        
        # Cache it
        self.section_cache[cache_key] = section
        return section
    
    def _get_or_create_standard(self, section: Section, standard_name: str) -> Standard:
        """Get or create standard (case-insensitive)."""
        # Check cache first
        cache_key = f"{section.id}:{standard_name.lower()}"
        if cache_key in self.standard_cache:
            return self.standard_cache[cache_key]
        
        # Try to find existing standard (case-insensitive)
        standard = Standard.objects.filter(
            section=section,
            name__iexact=standard_name
        ).first()
        
        if not standard:
            standard = Standard.objects.create(
                section=section,
                name=standard_name
            )
            self.result.standards_created += 1
        
        # Cache it
        self.standard_cache[cache_key] = standard
        return standard
    
    def _match_user(self, assigned_to: str) -> User:
        """Try to match a user by email or username."""
        if not assigned_to:
            return None
        
        # Try by email first
        user = User.objects.filter(email__iexact=assigned_to).first()
        if user:
            return user
        
        # Try by username
        user = User.objects.filter(username__iexact=assigned_to).first()
        return user
