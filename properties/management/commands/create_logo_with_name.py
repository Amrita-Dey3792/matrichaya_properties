from django.core.management.base import BaseCommand
from properties.models import NavbarImage
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a logo with custom name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            help='Name for the logo',
            default='Matrichaya Properties Ltd.'
        )
        parser.add_argument(
            '--image-path',
            type=str,
            help='Path to the logo image file',
            required=True
        )

    def handle(self, *args, **options):
        logo_name = options['name']
        image_path = options['image_path']
        
        # Check if image file exists
        if not os.path.exists(image_path):
            self.stdout.write(
                self.style.ERROR(f'Image file not found: {image_path}')
            )
            return
        
        # Deactivate existing logo
        NavbarImage.objects.filter(image_type='logo', is_active=True).update(is_active=False)
        
        # Create new logo
        try:
            with open(image_path, 'rb') as f:
                logo = NavbarImage.objects.create(
                    name=logo_name,
                    image_type='logo',
                    is_active=True,
                    order=0
                )
                logo.image.save(
                    os.path.basename(image_path),
                    f,
                    save=True
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created logo: "{logo_name}"')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Logo image: {logo.image.url}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating logo: {str(e)}')
            )
