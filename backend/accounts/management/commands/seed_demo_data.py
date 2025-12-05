"""
Management command to seed demo data for development.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Role, UserRole
from organizations.models import Department
from proformas.models import ProformaTemplate, ProformaSection, ProformaItem
from assignments.models import Assignment, ItemStatus
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for development'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding demo data...'))
        
        # Create roles if they don't exist
        roles = {}
        for role_name in ['SuperAdmin', 'QAAdmin', 'DepartmentCoordinator', 'Viewer']:
            role, _ = Role.objects.get_or_create(name=role_name)
            roles[role_name] = role
            self.stdout.write(self.style.SUCCESS(f'  Role: {role.get_name_display()}'))
        
        # Create departments
        dept1, _ = Department.objects.get_or_create(
            code='MED',
            defaults={'name': 'Medical Department'}
        )
        dept2, _ = Department.objects.get_or_create(
            code='SURG',
            defaults={'name': 'Surgery Department'}
        )
        dept3, _ = Department.objects.get_or_create(
            code='PED',
            defaults={'name': 'Pediatrics Department'}
        )
        self.stdout.write(self.style.SUCCESS(f'  Created {Department.objects.count()} departments'))
        
        # Create users
        users = {}
        
        # SuperAdmin
        superadmin, _ = User.objects.get_or_create(
            email='admin@accreditrack.local',
            defaults={
                'full_name': 'Super Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if not superadmin.has_usable_password():
            superadmin.set_password('admin123')
            superadmin.save()
        UserRole.objects.get_or_create(
            user=superadmin,
            role=roles['SuperAdmin']
        )
        users['admin'] = superadmin
        
        # QAAdmin
        qaadmin, _ = User.objects.get_or_create(
            email='qa@accreditrack.local',
            defaults={'full_name': 'QA Administrator'}
        )
        if not qaadmin.has_usable_password():
            qaadmin.set_password('qa123')
            qaadmin.save()
        UserRole.objects.get_or_create(
            user=qaadmin,
            role=roles['QAAdmin']
        )
        users['qa'] = qaadmin
        
        # Coordinators
        for dept, email_suffix in [(dept1, 'med'), (dept2, 'surg'), (dept3, 'ped')]:
            coordinator, _ = User.objects.get_or_create(
                email=f'coordinator.{email_suffix}@accreditrack.local',
                defaults={'full_name': f'{dept.name} Coordinator'}
            )
            if not coordinator.has_usable_password():
                coordinator.set_password('coord123')
                coordinator.save()
            UserRole.objects.get_or_create(
                user=coordinator,
                role=roles['DepartmentCoordinator'],
                department=dept
            )
            users[f'coord_{email_suffix}'] = coordinator
        
        self.stdout.write(self.style.SUCCESS(f'  Created {User.objects.count()} users'))
        
        # Create a proforma template
        template, _ = ProformaTemplate.objects.get_or_create(
            title='PMDC Accreditation Proforma 2024',
            defaults={
                'authority_name': 'PMDC',
                'description': 'Medical College Accreditation Requirements',
                'version': '1.0',
                'is_active': True,
            }
        )
        
        # Create sections
        section_a, _ = ProformaSection.objects.get_or_create(
            template=template,
            code='A',
            defaults={
                'title': 'Infrastructure and Facilities',
                'weight': 1,
            }
        )
        
        section_b, _ = ProformaSection.objects.get_or_create(
            template=template,
            code='B',
            defaults={
                'title': 'Faculty and Staff',
                'weight': 2,
            }
        )
        
        # Create items
        items_data = [
            (section_a, 'A.1', 'Adequate lecture halls with proper seating capacity', 'Building plans', 5),
            (section_a, 'A.2', 'Well-equipped laboratories for practical training', 'Lab inventory', 5),
            (section_a, 'A.3', 'Library with sufficient medical books and journals', 'Library catalog', 4),
            (section_b, 'B.1', 'Minimum required number of full-time faculty members', 'Faculty list', 5),
            (section_b, 'B.2', 'Faculty qualifications and certifications', 'CVs and certificates', 5),
        ]
        
        for section, code, text, evidence, importance in items_data:
            ProformaItem.objects.get_or_create(
                section=section,
                code=code,
                defaults={
                    'requirement_text': text,
                    'required_evidence_type': evidence,
                    'importance_level': importance,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Created template: {template.title}'))
        self.stdout.write(self.style.SUCCESS(f'  Created {ProformaSection.objects.filter(template=template).count()} sections'))
        self.stdout.write(self.style.SUCCESS(f'  Created {ProformaItem.objects.filter(section__template=template).count()} items'))
        
        # Create assignments
        due_date = date.today() + timedelta(days=90)
        for dept in [dept1, dept2]:
            assignment, created = Assignment.objects.get_or_create(
                proforma_template=template,
                department=dept,
                defaults={
                    'start_date': date.today(),
                    'due_date': due_date,
                    'status': 'InProgress',
                }
            )
            
            if created:
                # Auto-create ItemStatus records
                items = ProformaItem.objects.filter(section__template=template)
                ItemStatus.objects.bulk_create([
                    ItemStatus(
                        assignment=assignment,
                        proforma_item=item,
                        status='NotStarted',
                        completion_percent=0
                    )
                    for item in items
                ])
                self.stdout.write(self.style.SUCCESS(f'  Created assignment for {dept.name}'))
        
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write(self.style.SUCCESS('  SuperAdmin: admin@accreditrack.local / admin123'))
        self.stdout.write(self.style.SUCCESS('  QAAdmin: qa@accreditrack.local / qa123'))
        self.stdout.write(self.style.SUCCESS('  Coordinators: coordinator.med@accreditrack.local / coord123'))
