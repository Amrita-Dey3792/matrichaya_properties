from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from properties.image_utils import resize_image, get_image_dimensions
import os


class Command(BaseCommand):
    help = 'Test image processing functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing image processing functionality...')
        
        # Create a test image file (you can replace this with an actual image path)
        test_image_path = 'media/carousel/test_image.jpg'
        
        if os.path.exists(test_image_path):
            with open(test_image_path, 'rb') as f:
                image_data = f.read()
                uploaded_file = SimpleUploadedFile(
                    'test_image.jpg',
                    image_data,
                    content_type='image/jpeg'
                )
                
                # Test getting dimensions
                width, height = get_image_dimensions(uploaded_file)
                self.stdout.write(f'Original image dimensions: {width}x{height}')
                
                # Test resizing
                processed_image = resize_image(uploaded_file, target_width=1200, target_height=650)
                
                # Get processed dimensions
                processed_width, processed_height = get_image_dimensions(processed_image)
                self.stdout.write(f'Processed image dimensions: {processed_width}x{processed_height}')
                
                self.stdout.write(
                    self.style.SUCCESS('Image processing test completed successfully!')
                )
        else:
            self.stdout.write(
                self.style.WARNING('No test image found. Please add an image to media/carousel/test_image.jpg to test.')
            )
