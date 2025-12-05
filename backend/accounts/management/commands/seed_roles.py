"""
Management command to seed default roles.
"""
from django.core.management.base import BaseCommand
from accounts.models import Role


class Command(BaseCommand):
    help = 'Seed default roles for the application'
    
    def handle(self, *args, **options):
        roles = [
            {'name': 'SuperAdmin', 'description': 'Super Administrator with full access'},
            {'name': 'QAAdmin', 'description': 'QA Administrator who manages proformas and assignments'},
            {'name': 'DepartmentCoordinator', 'description': 'Department Coordinator who manages assignments for their department'},
            {'name': 'Viewer', 'description': 'Viewer with read-only access'},
        ]
        
        created_count = 0
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.get_name_display()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.get_name_display()}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSeeded {created_count} new roles. Total roles: {Role.objects.count()}')
        )
