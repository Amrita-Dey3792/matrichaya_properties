from django.core.management.base import BaseCommand
from properties.models import CarouselSlide


class Command(BaseCommand):
    help = 'Create sample carousel slides'

    def handle(self, *args, **options):
        # Clear existing slides
        CarouselSlide.objects.all().delete()
        
        # Create sample carousel slides
        slides_data = [
            {
                'title': 'Welcome to Matrichaya Properties',
                'subtitle': 'Your Trusted Real Estate Partner',
                'description': 'Discover premium land properties and residential projects across Bangladesh with Matrichaya Properties Ltd.',
                'button_text': 'Explore Properties',
                'button_url': '/land-properties/',
                'slide_type': 'hero',
                'background_color': '#22c55e',
                'is_active': True,
                'order': 1
            },
            {
                'title': 'Premium Land Projects',
                'subtitle': 'Invest in Your Future',
                'description': 'Choose from our carefully selected land properties in prime locations with modern amenities and infrastructure.',
                'button_text': 'View Projects',
                'button_url': '/land-properties/',
                'slide_type': 'feature',
                'background_color': '#3b82f6',
                'is_active': True,
                'order': 2
            },
            {
                'title': 'Expert Real Estate Services',
                'subtitle': 'Professional Guidance',
                'description': 'Get expert advice and support throughout your property investment journey with our experienced team.',
                'button_text': 'Contact Us',
                'button_url': '/contact/',
                'slide_type': 'service',
                'background_color': '#8b5cf6',
                'is_active': True,
                'order': 3
            },
            {
                'title': 'Prime Locations',
                'subtitle': 'Strategic Investment Opportunities',
                'description': 'Invest in land properties located in developing areas with excellent growth potential and connectivity.',
                'button_text': 'Learn More',
                'button_url': '/land-properties/',
                'slide_type': 'location',
                'background_color': '#f59e0b',
                'is_active': True,
                'order': 4
            },
            {
                'title': 'Customer Satisfaction',
                'subtitle': 'Your Success is Our Priority',
                'description': 'Join hundreds of satisfied customers who have successfully invested in properties through Matrichaya Properties.',
                'button_text': 'Get Started',
                'button_url': '/contact/',
                'slide_type': 'testimonial',
                'background_color': '#ef4444',
                'is_active': True,
                'order': 5
            }
        ]
        
        for slide_data in slides_data:
            CarouselSlide.objects.create(**slide_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(slides_data)} carousel slides')
        )
