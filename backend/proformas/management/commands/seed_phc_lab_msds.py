"""
Management command to seed PHC MSDS Pathology / Clinical Laboratories checklist template.
"""
import os
import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from modules.models import Module
from proformas.models import ProformaTemplate, ProformaSection, ProformaItem


class Command(BaseCommand):
    help = 'Seed PHC MSDS Pathology / Clinical Laboratories checklist template from YAML'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yaml-file',
            type=str,
            default=None,
            help='Path to YAML file (default: data/phc_msds_lab_2018.yaml)',
        )

    def handle(self, *args, **options):
        # Determine YAML file path
        if options['yaml_file']:
            yaml_path = options['yaml_file']
        else:
            # Default to data directory in proformas app
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            yaml_path = os.path.join(app_dir, 'proformas', 'data', 'phc_msds_lab_2018.yaml')
        
        if not os.path.exists(yaml_path):
            self.stdout.write(self.style.ERROR(f'YAML file not found: {yaml_path}'))
            return
        
        self.stdout.write(f'Loading YAML from: {yaml_path}')
        
        # Load YAML file
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        template_data = data['template']
        categories_data = data['categories']
        
        # Get or create module
        module_code = template_data['module']
        module, module_created = Module.objects.get_or_create(
            code=module_code,
            defaults={
                'display_name': f'PHC Laboratory',
                'description': f'Primary Healthcare Laboratory Accreditation Module',
                'is_active': True,
            }
        )
        
        if module_created:
            self.stdout.write(self.style.SUCCESS(f'Created module: {module.display_name}'))
        else:
            self.stdout.write(f'Module {module.display_name} already exists')
        
        # Create or update template
        template_code = template_data['code']
        template, template_created = ProformaTemplate.objects.get_or_create(
            code=template_code,
            defaults={
                'title': template_data['name'],
                'authority_name': template_data['authority'],
                'description': template_data.get('description', ''),
                'version': template_data['version'],
                'is_active': True,
                'module': module,
            }
        )
        
        if template_created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {template.title}'))
        else:
            self.stdout.write(f'Template {template.title} already exists, updating...')
            template.title = template_data['name']
            template.authority_name = template_data['authority']
            template.description = template_data.get('description', '')
            template.version = template_data['version']
            template.module = module
            template.save()
        
        # Process categories, standards, and indicators
        with transaction.atomic():
            categories_count = 0
            standards_count = 0
            indicators_count = 0
            
            # Track existing sections to avoid duplicates
            existing_sections = {}
            
            for cat_idx, category_data in enumerate(categories_data):
                cat_code = category_data['code']
                cat_title = category_data['title']
                
                # Create or update category section
                category_section, cat_created = ProformaSection.objects.get_or_create(
                    template=template,
                    code=cat_code,
                    defaults={
                        'title': cat_title,
                        'section_type': 'CATEGORY',
                        'weight': cat_idx + 1,
                        'parent': None,
                    }
                )
                
                if cat_created:
                    categories_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  Created category: {category_section.code} - {category_section.title}'))
                else:
                    # Update existing category
                    category_section.title = cat_title
                    category_section.section_type = 'CATEGORY'
                    category_section.weight = cat_idx + 1
                    category_section.parent = None
                    category_section.save()
                    self.stdout.write(f'  Updated category: {category_section.code} - {category_section.title}')
                
                existing_sections[cat_code] = category_section
                
                # Process standards under this category
                standards_data = category_data.get('standards', [])
                for std_idx, standard_data in enumerate(standards_data):
                    std_code = standard_data['code']
                    std_title = standard_data['title']
                    
                    # Create or update standard section
                    standard_section, std_created = ProformaSection.objects.get_or_create(
                        template=template,
                        code=std_code,
                        defaults={
                            'title': std_title,
                            'section_type': 'STANDARD',
                            'weight': std_idx + 1,
                            'parent': category_section,
                        }
                    )
                    
                    if std_created:
                        standards_count += 1
                        self.stdout.write(self.style.SUCCESS(f'    Created standard: {standard_section.code} - {standard_section.title}'))
                    else:
                        # Update existing standard
                        standard_section.title = std_title
                        standard_section.section_type = 'STANDARD'
                        standard_section.weight = std_idx + 1
                        standard_section.parent = category_section
                        standard_section.save()
                        self.stdout.write(f'    Updated standard: {standard_section.code} - {standard_section.title}')
                    
                    existing_sections[std_code] = standard_section
                    
                    # Process indicators under this standard
                    indicators_data = standard_data.get('indicators', [])
                    for ind_idx, indicator_data in enumerate(indicators_data):
                        ind_code = indicator_data['code']
                        ind_text = indicator_data['text']
                        
                        # Create or update indicator item
                        indicator_item, ind_created = ProformaItem.objects.get_or_create(
                            section=standard_section,
                            code=ind_code,
                            defaults={
                                'requirement_text': ind_text,
                                'max_score': indicator_data.get('max_score', 10),
                                'weightage_percent': indicator_data.get('weightage_percent', 100),
                                'is_licensing_critical': indicator_data.get('is_licensing_critical', False),
                                'implementation_criteria': indicator_data.get('implementation_criteria', ''),
                            }
                        )
                        
                        if ind_created:
                            indicators_count += 1
                            self.stdout.write(self.style.SUCCESS(f'      Created indicator: {indicator_item.code}'))
                        else:
                            # Update existing indicator
                            indicator_item.requirement_text = ind_text
                            indicator_item.max_score = indicator_data.get('max_score', 10)
                            indicator_item.weightage_percent = indicator_data.get('weightage_percent', 100)
                            indicator_item.is_licensing_critical = indicator_data.get('is_licensing_critical', False)
                            indicator_item.implementation_criteria = indicator_data.get('implementation_criteria', '')
                            indicator_item.save()
                            self.stdout.write(f'      Updated indicator: {indicator_item.code}')
            
            # Clean up orphaned sections (sections not in YAML but exist in DB for this template)
            # We'll skip this for now to avoid data loss, but it could be added as an option
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('PHC MSDS Lab 2018 Template Seeding Complete!'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'Template: {template.title} (Code: {template.code})')
            self.stdout.write(f'Module: {module.display_name} ({module.code})')
            self.stdout.write(f'Categories: {categories_count} created/updated')
            self.stdout.write(f'Standards: {standards_count} created/updated')
            self.stdout.write(f'Indicators: {indicators_count} created/updated')
            self.stdout.write(f'Total Sections: {template.sections.count()}')
            self.stdout.write(f'Total Items: {ProformaItem.objects.filter(section__template=template).count()}')
            self.stdout.write(self.style.SUCCESS('='*60))
