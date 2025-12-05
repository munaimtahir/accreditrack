"""
Management command to seed PHC Laboratory module with sample template structure.
"""
from django.core.management.base import BaseCommand
from modules.models import Module
from proformas.models import ProformaTemplate, ProformaSection, ProformaItem


class Command(BaseCommand):
    help = 'Seed PHC Laboratory module with sample template structure'

    def handle(self, *args, **options):
        self.stdout.write('Creating PHC Laboratory module...')
        
        # Create or get PHC-LAB module
        module, created = Module.objects.get_or_create(
            code='PHC-LAB',
            defaults={
                'display_name': 'PHC Laboratory',
                'description': 'Primary Healthcare Laboratory Accreditation Module',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created module: {module.display_name}'))
        else:
            self.stdout.write(f'Module {module.display_name} already exists')
        
        # Create PHC Lab template
        template, created = ProformaTemplate.objects.get_or_create(
            title='PHC Laboratory Accreditation Standards',
            authority_name='PMDC',
            defaults={
                'description': 'Primary Healthcare Laboratory accreditation standards and requirements',
                'version': '1.0',
                'is_active': True,
                'module': module,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {template.title}'))
        else:
            self.stdout.write(f'Template {template.title} already exists')
            template.module = module
            template.save()
        
        # Define sample categories/sections (ROM, FMS, etc.)
        sections_data = [
            {
                'code': 'ROM',
                'title': 'Resource and Organization Management',
                'weight': 1,
                'items': [
                    {
                        'code': 'Ind 1',
                        'requirement_text': 'The laboratory shall have a documented organizational structure with clear lines of authority and responsibility.',
                        'required_evidence_type': 'Organizational chart, job descriptions',
                        'importance_level': 5,
                        'implementation_criteria': 'Document organizational structure, define roles and responsibilities',
                    },
                    {
                        'code': 'Ind 2',
                        'requirement_text': 'The laboratory shall have qualified personnel with appropriate education and training.',
                        'required_evidence_type': 'CVs, certificates, training records',
                        'importance_level': 5,
                        'implementation_criteria': 'Maintain personnel records, ensure qualifications meet requirements',
                    },
                ],
            },
            {
                'code': 'FMS',
                'title': 'Facility Management and Safety',
                'weight': 2,
                'items': [
                    {
                        'code': 'Ind 1',
                        'requirement_text': 'The laboratory shall have adequate space and facilities for all activities.',
                        'required_evidence_type': 'Floor plans, facility photos',
                        'importance_level': 4,
                        'implementation_criteria': 'Ensure adequate space allocation, proper ventilation, lighting',
                    },
                    {
                        'code': 'Ind 2',
                        'requirement_text': 'The laboratory shall have appropriate safety measures and emergency procedures.',
                        'required_evidence_type': 'Safety manual, emergency procedures, incident reports',
                        'importance_level': 5,
                        'implementation_criteria': 'Develop safety protocols, conduct safety training, maintain safety equipment',
                    },
                ],
            },
            {
                'code': 'ROM-1',
                'title': 'Quality Management System',
                'weight': 3,
                'items': [
                    {
                        'code': 'Ind 1',
                        'requirement_text': 'The laboratory shall have a documented quality management system.',
                        'required_evidence_type': 'Quality manual, procedures, records',
                        'importance_level': 5,
                        'implementation_criteria': 'Develop quality manual, establish procedures, maintain records',
                    },
                    {
                        'code': 'Ind 2',
                        'requirement_text': 'The laboratory shall conduct internal quality audits regularly.',
                        'required_evidence_type': 'Audit reports, corrective action records',
                        'importance_level': 4,
                        'implementation_criteria': 'Schedule regular audits, document findings, implement corrective actions',
                    },
                ],
            },
        ]
        
        # Create sections and items
        for section_data in sections_data:
            section, created = ProformaSection.objects.get_or_create(
                template=template,
                code=section_data['code'],
                defaults={
                    'title': section_data['title'],
                    'weight': section_data['weight'],
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created section: {section.code} - {section.title}'))
            else:
                self.stdout.write(f'  Section {section.code} already exists')
            
            # Create items for this section
            for item_data in section_data['items']:
                item, created = ProformaItem.objects.get_or_create(
                    section=section,
                    code=item_data['code'],
                    defaults={
                        'requirement_text': item_data['requirement_text'],
                        'required_evidence_type': item_data.get('required_evidence_type', ''),
                        'importance_level': item_data.get('importance_level'),
                        'implementation_criteria': item_data.get('implementation_criteria', ''),
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'    Created item: {item.code}'))
        
        self.stdout.write(self.style.SUCCESS('\nSuccessfully seeded PHC Laboratory module!'))
        self.stdout.write(f'Module: {module.display_name} ({module.code})')
        self.stdout.write(f'Template: {template.title}')
        self.stdout.write(f'Sections: {template.sections.count()}')
        self.stdout.write(f'Total Items: {ProformaItem.objects.filter(section__template=template).count()}')
