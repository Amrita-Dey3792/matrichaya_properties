from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from custom_admin.models import AdminActivity


class Command(BaseCommand):
    help = 'Create sample admin activities for testing'

    def handle(self, *args, **options):
        # Create admin user if doesn't exist
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@matrichaya.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created admin user: admin/admin123')
            )

        # Sample activities data
        activities_data = [
            # Land Property activities
            {'action': 'create', 'model_name': 'LandProperty', 'description': 'Created new land property: Green Valley Plots'},
            {'action': 'update', 'model_name': 'LandProperty', 'description': 'Updated land property: Riverside Development'},
            {'action': 'view', 'model_name': 'LandProperty', 'description': 'Viewed land properties with filters'},
            
            # Carousel activities
            {'action': 'create', 'model_name': 'CarouselSlide', 'description': 'Created new carousel slide: Summer Promotion'},
            {'action': 'update', 'model_name': 'CarouselSlide', 'description': 'Updated carousel slide: Winter Campaign'},
            {'action': 'delete', 'model_name': 'CarouselSlide', 'description': 'Deleted carousel slide: Old Banner'},
            
            # Navbar activities
            {'action': 'update', 'model_name': 'NavbarImage', 'description': 'Updated navbar logo image'},
            {'action': 'update', 'model_name': 'NavbarImage', 'description': 'Updated banner image'},
            
            # Admin activities
            {'action': 'login', 'model_name': 'Admin', 'description': 'Admin logged in successfully'},
            {'action': 'logout', 'model_name': 'Admin', 'description': 'Admin logged out'},
            {'action': 'view', 'model_name': 'AdminActivity', 'description': 'Viewed admin activities (page 1)'},
            
            # Contact activities
            {'action': 'create', 'model_name': 'ContactMessage', 'description': 'New contact message received from customer'},
            {'action': 'view', 'model_name': 'ContactMessage', 'description': 'Viewed contact messages'},
            
            # Dashboard activities
            {'action': 'view', 'model_name': 'Dashboard', 'description': 'Accessed admin dashboard'},
            {'action': 'view', 'model_name': 'Dashboard', 'description': 'Viewed statistics and recent activities'},
        ]

        # Create activities with random timestamps over the last 30 days
        now = timezone.now()
        created_count = 0
        
        for activity_data in activities_data:
            # Random timestamp within last 30 days
            random_days = random.randint(0, 30)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            
            timestamp = now - timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            # Random IP address
            ip_address = f"192.168.1.{random.randint(1, 255)}"
            
            AdminActivity.objects.create(
                admin=admin_user,
                action=activity_data['action'],
                model_name=activity_data['model_name'],
                description=activity_data['description'],
                ip_address=ip_address,
                timestamp=timestamp
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample admin activities')
        )
