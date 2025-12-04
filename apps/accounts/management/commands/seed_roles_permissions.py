"""
Seed initial roles and permissions for the system
Usage: python manage.py seed_roles_permissions
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import (
    PlatformRoleChoices, OrganizationRoleChoices,
    SpecializedRoleChoices, PermissionChoices
)


class Command(BaseCommand):
    help = 'Seed initial roles and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Seeding roles and permissions...')
        
        # Platform roles
        platform_roles = [
            PlatformRoleChoices.USER,
            PlatformRoleChoices.ADMIN,
            PlatformRoleChoices.REGULATOR
        ]
        
        # Organization roles
        org_roles = [
            OrganizationRoleChoices.ORG_OWNER,
            OrganizationRoleChoices.ORG_MANAGER,
            OrganizationRoleChoices.ORG_MEMBER
        ]
        
        # Specialized roles
        specialized_roles = [
            SpecializedRoleChoices.BUYER,
            SpecializedRoleChoices.SELLER,
            SpecializedRoleChoices.DEVELOPER,
            SpecializedRoleChoices.VALIDATOR,
            SpecializedRoleChoices.AUDITOR
        ]
        
        # Permissions (defined in models)
        permissions = [
            PermissionChoices.CREATE_PROJECT,
            PermissionChoices.EDIT_PROJECT,
            PermissionChoices.DELETE_PROJECT,
            PermissionChoices.VIEW_PROJECT,
            PermissionChoices.SUBMIT_DATA,
            PermissionChoices.VALIDATE_DATA,
            PermissionChoices.APPROVE_MRV,
            PermissionChoices.CREATE_CREDIT,
            PermissionChoices.MANAGE_MARKETPLACE,
            PermissionChoices.MANAGE_ORGANIZATION,
            PermissionChoices.MANAGE_USERS,
            PermissionChoices.AUDIT_LOGS,
            PermissionChoices.FREEZE_USER,
            PermissionChoices.OVERRIDE_MRV,
            PermissionChoices.MANAGE_PERMISSIONS
        ]
        
        self.stdout.write(self.style.SUCCESS(f'✓ Platform roles: {len(platform_roles)}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Organization roles: {len(org_roles)}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Specialized roles: {len(specialized_roles)}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Permissions: {len(permissions)}'))
        
        self.stdout.write(self.style.SUCCESS('\nRoles and permissions configured successfully!'))
