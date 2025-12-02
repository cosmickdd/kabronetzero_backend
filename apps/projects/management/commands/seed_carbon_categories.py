"""
Management command to seed carbon categories into MongoDB
"""

from django.core.management.base import BaseCommand, CommandError
from mongoengine import connect, disconnect
import os
import django

# Setup Django
django.setup()

# Import after Django setup
from projects.models import CarbonCategory


class Command(BaseCommand):
    help = 'Seed initial carbon categories into the database'

    def handle(self, *args, **options):
        """Execute the seeding command"""
        try:
            # Connect to MongoDB
            from config.settings import MONGO_URI
            connect(host=MONGO_URI)
            
            # Define categories
            categories = [
                {
                    'code': 'BLUE',
                    'name': 'Coastal & Marine',
                    'description': 'Coastal protection, mangrove restoration, marine ecosystem projects',
                    'icon_color': '#0066CC',
                    'default_offset': 1.0,
                },
                {
                    'code': 'GREEN',
                    'name': 'Forest & Land',
                    'description': 'Reforestation, afforestation, forest conservation, land restoration',
                    'icon_color': '#00AA00',
                    'default_offset': 1.0,
                },
                {
                    'code': 'BROWN',
                    'name': 'Renewable Energy',
                    'description': 'Solar, wind, hydro, geothermal, biogas energy projects',
                    'icon_color': '#DD6600',
                    'default_offset': 1.0,
                },
                {
                    'code': 'GREY',
                    'name': 'Industrial & Efficiency',
                    'description': 'Energy efficiency, industrial process improvements, waste reduction',
                    'icon_color': '#888888',
                    'default_offset': 1.0,
                },
                {
                    'code': 'BIO',
                    'name': 'Agriculture & Biodiversity',
                    'description': 'Regenerative agriculture, biodiversity conservation, soil carbon',
                    'icon_color': '#8B4513',
                    'default_offset': 1.0,
                }
            ]
            
            # Check if categories already exist
            existing_count = CarbonCategory.objects.count()
            if existing_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Found {existing_count} existing categories, skipping seed')
                )
                return
            
            # Create categories
            created_count = 0
            for category_data in categories:
                category = CarbonCategory(**category_data)
                category.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_data["name"]} ({category_data["code"]})')
                )
            
            disconnect()
            
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully seeded {created_count} carbon categories')
            )
            
        except Exception as e:
            raise CommandError(f'Error seeding categories: {str(e)}')
