from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import CompanyInfo, LandProperty, ContactMessage


def home(request):
    """Home page view with featured land projects"""
    # Get featured land projects, if none exist, get any active land projects
    featured_land_projects = LandProperty.objects.filter(is_featured=True, is_active=True)[:3]
    
    # If no featured projects, get any active land projects
    if not featured_land_projects.exists():
        featured_land_projects = LandProperty.objects.filter(is_active=True)[:3]
    
    company_info = CompanyInfo.objects.first()
    
    context = {
        'featured_land_projects': featured_land_projects,
        'company_info': company_info,
        'has_land_projects': LandProperty.objects.filter(is_active=True).exists(),
    }
    return render(request, 'properties/home.html', context)


def land_properties(request):
    """Land properties page with filtering"""
    land_properties_list = LandProperty.objects.filter(is_active=True)
    
    # Filtering
    project_status = request.GET.get('status', '')
    property_type = request.GET.get('type', '')
    division = request.GET.get('division', '')
    district = request.GET.get('district', '')
    area = request.GET.get('area', '')
    search = request.GET.get('search', '')
    
    # Debug: Print received parameters
    print(f"Received filters - Status: {project_status}, Type: {property_type}, Division: {division}, District: {district}, Area: {area}")
    
    if project_status:
        land_properties_list = land_properties_list.filter(project_status=project_status)
    
    if property_type:
        land_properties_list = land_properties_list.filter(property_type=property_type)
    
    if division:
        land_properties_list = land_properties_list.filter(division=division)
    
    if district:
        land_properties_list = land_properties_list.filter(district__icontains=district)
    
    if area:
        land_properties_list = land_properties_list.filter(area_name__icontains=area)
    
    if search:
        land_properties_list = land_properties_list.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Check if user wants to view all projects
    view_mode = request.GET.get('view', 'paginated')
    
    if view_mode == 'all':
        # Show all projects without pagination
        page_obj = land_properties_list
        paginator = None
    else:
        # Pagination
        paginator = Paginator(land_properties_list, 6)  # 6 items per page for 2x3 grid
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    
    # Get unique districts for the current division
    districts = []
    if division:
        districts = LandProperty.objects.filter(
            division=division, 
            is_active=True
        ).values_list('district', flat=True).distinct().order_by('district')
    
    # Get unique areas for the current district
    areas = []
    if district:
        areas = LandProperty.objects.filter(
            district__icontains=district, 
            is_active=True
        ).values_list('area_name', flat=True).distinct().order_by('area_name')
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'view_mode': view_mode,
        'project_status': project_status,
        'property_type': property_type,
        'division': division,
        'district': district,
        'area': area,
        'search': search,
        'districts': districts,
        'areas': areas,
        'project_statuses': LandProperty.PROJECT_STATUS,
        'property_types': LandProperty.PROPERTY_TYPE,
        'divisions': LandProperty.DIVISIONS,
    }
    return render(request, 'properties/land_properties.html', context)


def land_property_detail(request, pk):
    """Land property detail view"""
    land_property = get_object_or_404(LandProperty, pk=pk, is_active=True)
    
    # Get related properties (same division or district)
    related_properties = LandProperty.objects.filter(
        is_active=True
    ).exclude(pk=pk).filter(
        Q(division=land_property.division) | Q(district=land_property.district)
    )[:3]
    
    context = {
        'land_property': land_property,
        'related_properties': related_properties,
    }
    return render(request, 'properties/land_property_detail.html', context)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle form submission
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        property_type = request.POST.get('property_type', '')
        budget = request.POST.get('budget', '')
        message = request.POST.get('message', '').strip()
        newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
        
        # Basic validation
        errors = []
        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')
        if not email:
            errors.append('Email is required')
        elif '@' not in email:
            errors.append('Please enter a valid email address')
        if not phone:
            errors.append('Phone number is required')
        if not message:
            errors.append('Message is required')
        
        if errors:
            messages.error(request, 'Please correct the following errors:')
            for error in errors:
                messages.error(request, error)
        else:
            # Save contact message
            contact_message = ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                property_type=property_type,
                budget=budget,
                message=message,
                newsletter_subscription=newsletter_subscription,
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    
    context = {
        'property_types': ContactMessage.PROPERTY_INTEREST_CHOICES,
        'budget_ranges': ContactMessage.BUDGET_CHOICES,
    }
    return render(request, 'properties/contact.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def contact_ajax(request):
    """AJAX contact form submission"""
    try:
        data = json.loads(request.body)
        
        # Extract form data
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        property_type = data.get('property_type', '')
        budget = data.get('budget', '')
        message = data.get('message', '').strip()
        newsletter_subscription = data.get('newsletter_subscription', False)
        
        # Validation
        errors = []
        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')
        if not email:
            errors.append('Email is required')
        elif '@' not in email:
            errors.append('Please enter a valid email address')
        if not phone:
            errors.append('Phone number is required')
        if not message:
            errors.append('Message is required')
        
        if errors:
            return JsonResponse({
                'success': False,
                'errors': errors
            })
        
        # Save contact message
        contact_message = ContactMessage.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            property_type=property_type,
            budget=budget,
            message=message,
            newsletter_subscription=newsletter_subscription,
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your message! We will get back to you soon.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'errors': ['Invalid request data']
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': ['An error occurred. Please try again.']
        })