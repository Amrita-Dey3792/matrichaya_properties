from django.core.management.base import BaseCommand
from django.utils import timezone
from properties.models import LandProperty


class Command(BaseCommand):
    help = 'Create sample land properties for testing'

    def handle(self, *args, **options):
        sample_properties = [
            {
                'name': 'Polash Nagar',
                'area': '150 katha',
                'location': 'Keraniganj, Dhaka, Dhaka',
                'division': 'dhaka',
                'district': 'Dhaka',
                'area_name': 'Keraniganj',
                'description': 'A premium residential project in Keraniganj with modern amenities and excellent connectivity to Dhaka city.',
                'project_status': 'ongoing',
                'property_type': 'residential',
                'price_per_katha': 2500000,
                'total_plots': 50,
                'available_plots': 15,
                'amenities': 'Road Access, Electricity, Water Supply, Security, Park, Mosque, School Nearby',
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'South Dhaka Model Town',
                'area': '1200 katha',
                'location': 'Sirajdikhan, Munshiganj, Dhaka',
                'division': 'dhaka',
                'district': 'Munshiganj',
                'area_name': 'Sirajdikhan',
                'description': 'A large-scale residential development project featuring modern infrastructure and community facilities.',
                'project_status': 'ongoing',
                'property_type': 'residential',
                'price_per_katha': 1800000,
                'total_plots': 200,
                'available_plots': 45,
                'amenities': 'Wide Roads, Underground Electricity, Water Treatment Plant, Security System, Community Center, Market',
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Dishari Golden City',
                'area': '150 katha',
                'location': 'Keraniganj, Dhaka, Dhaka',
                'division': 'dhaka',
                'district': 'Dhaka',
                'area_name': 'Keraniganj',
                'description': 'An exclusive residential project with luxury amenities and premium location benefits.',
                'project_status': 'completed',
                'property_type': 'residential',
                'price_per_katha': 3200000,
                'total_plots': 30,
                'available_plots': 2,
                'amenities': 'Premium Roads, Underground Utilities, Swimming Pool, Gym, Club House, 24/7 Security',
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Chittagong Business Hub',
                'area': '500 katha',
                'location': 'Panchlaish, Chittagong, Chittagong',
                'division': 'chittagong',
                'district': 'Chittagong',
                'area_name': 'Panchlaish',
                'description': 'A commercial development project in the heart of Chittagong with modern office spaces and retail outlets.',
                'project_status': 'ongoing',
                'property_type': 'commercial',
                'price_per_katha': 4500000,
                'total_plots': 80,
                'available_plots': 25,
                'amenities': 'Commercial Roads, High-Speed Internet, Parking Facility, Security, Banking Zone, Food Court',
                'is_featured': False,
                'is_active': True,
            },
            {
                'name': 'Sylhet Garden City',
                'area': '300 katha',
                'location': 'Zakiganj, Sylhet, Sylhet',
                'division': 'sylhet',
                'district': 'Sylhet',
                'area_name': 'Zakiganj',
                'description': 'A green residential project emphasizing natural beauty and sustainable living.',
                'project_status': 'upcoming',
                'property_type': 'residential',
                'price_per_katha': 2200000,
                'total_plots': 60,
                'available_plots': 60,
                'amenities': 'Green Roads, Solar Power, Rainwater Harvesting, Garden, Playground, Eco-Friendly Design',
                'is_featured': False,
                'is_active': True,
            },
            {
                'name': 'Rajshahi Tech Park',
                'area': '400 katha',
                'location': 'Bagha, Rajshahi, Rajshahi',
                'division': 'rajshahi',
                'district': 'Rajshahi',
                'area_name': 'Bagha',
                'description': 'A technology-focused commercial development with modern infrastructure for IT companies.',
                'project_status': 'ongoing',
                'property_type': 'commercial',
                'price_per_katha': 2800000,
                'total_plots': 40,
                'available_plots': 12,
                'amenities': 'Fiber Optic Internet, Backup Power, Conference Rooms, Cafeteria, Parking, Security',
                'is_featured': False,
                'is_active': True,
            },
            {
                'name': 'Khulna Riverside',
                'area': '200 katha',
                'location': 'Terokhada, Khulna, Khulna',
                'division': 'khulna',
                'district': 'Khulna',
                'area_name': 'Terokhada',
                'description': 'A waterfront residential project with beautiful river views and recreational facilities.',
                'project_status': 'ongoing',
                'property_type': 'residential',
                'price_per_katha': 1900000,
                'total_plots': 35,
                'available_plots': 8,
                'amenities': 'River View, Boat Jetty, Walking Trail, Park, Security, Water Sports Facility',
                'is_featured': True,
                'is_active': True,
            },
            {
                'name': 'Barisal Green Valley',
                'area': '250 katha',
                'location': 'Wazirpur, Barisal, Barisal',
                'division': 'barisal',
                'district': 'Barisal',
                'area_name': 'Wazirpur',
                'description': 'An eco-friendly residential project with emphasis on green living and sustainability.',
                'project_status': 'upcoming',
                'property_type': 'residential',
                'price_per_katha': 1600000,
                'total_plots': 45,
                'available_plots': 45,
                'amenities': 'Green Infrastructure, Solar Panels, Organic Garden, Cycling Track, Eco-Friendly Materials',
                'is_featured': False,
                'is_active': True,
            }
        ]

        created_count = 0
        for prop_data in sample_properties:
            # Check if property already exists
            if not LandProperty.objects.filter(name=prop_data['name']).exists():
                LandProperty.objects.create(**prop_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created land property: {prop_data["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Land property already exists: {prop_data["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample land properties!')
        )
