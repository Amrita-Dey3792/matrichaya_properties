from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os

from properties.models import CompanyInfo, NavbarImage, CarouselSlide, LandProperty, ContactMessage
from properties.image_utils import resize_image, delete_image_file
from .models import AdminProfile, AdminActivity
from django.contrib.auth.hashers import check_password, make_password


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_admin_activity(admin, action, model_name, description, request, object_id=None):
    """Log admin activity"""
    AdminActivity.objects.create(
        admin=admin,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


def admin_login(request):
    """Custom admin login"""
    if request.user.is_authenticated:
        return redirect('custom_admin:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            log_admin_activity(user, 'login', 'Admin', f'Admin logged in', request)
            messages.success(request, 'Welcome to the admin panel!')
            return redirect('custom_admin:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'custom_admin/login.html')


@login_required
def admin_logout(request):
    """Custom admin logout"""
    log_admin_activity(request.user, 'logout', 'Admin', f'Admin logged out', request)
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('custom_admin:login')


@login_required
def dashboard(request):
    """Admin dashboard with statistics"""
    
    # Handle sample data creation
    if request.method == 'POST' and request.POST.get('action') == 'create_sample_data':
        from django.core.management import call_command
        try:
            call_command('create_sample_land_properties')
            messages.success(request, 'Sample land properties created successfully!')
            log_admin_activity(request.user, 'create', 'LandProperty', 'Created sample land properties', request)
        except Exception as e:
            messages.error(request, f'Error creating sample data: {str(e)}')
        return redirect('custom_admin:dashboard')
    
    # Get statistics
    stats = {
        'total_land_properties': LandProperty.objects.count(),
        'featured_land_properties': LandProperty.objects.filter(is_featured=True).count(),
        'active_land_properties': LandProperty.objects.filter(is_active=True).count(),
        'logo_count': NavbarImage.objects.filter(image_type='logo').count(),
        'active_logo_count': NavbarImage.objects.filter(image_type='logo', is_active=True).count(),
        'carousel_slides': CarouselSlide.objects.count(),
        'active_carousel_slides': CarouselSlide.objects.filter(is_active=True).count(),
        'total_contact_messages': ContactMessage.objects.count(),
        'new_contact_messages': ContactMessage.objects.filter(status='new').count(),
    }
    
    # Recent activities
    recent_activities = AdminActivity.objects.select_related('admin').order_by('-timestamp')[:10]
    
    # Recent land properties
    recent_land_properties = LandProperty.objects.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_activities': recent_activities,
        'recent_land_properties': recent_land_properties,
    }
    
    log_admin_activity(request.user, 'view', 'Dashboard', 'Viewed admin dashboard', request)
    return render(request, 'custom_admin/dashboard.html', context)




@login_required
def logo_upload(request):
    """Manage logo uploads"""
    logos = NavbarImage.objects.filter(image_type='logo').order_by('order', '-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'upload':
            try:
                # Deactivate all existing logos when uploading new one
                NavbarImage.objects.filter(image_type='logo', is_active=True).update(is_active=False)
                
                logo_obj = NavbarImage.objects.create(
                    name=request.POST.get('name', 'Company Logo'),
                    image_type='logo',
                    image=request.FILES['image'],
                    is_active=True,  # New logo is always active
                    order=0,
                )
                log_admin_activity(request.user, 'create', 'NavbarImage', f'Uploaded logo: {logo_obj.name}', request, logo_obj.id)
                messages.success(request, f'Logo "{logo_obj.name}" uploaded successfully!')
            except Exception as e:
                messages.error(request, f'Error uploading logo: {str(e)}')
        
        elif action == 'toggle_active':
            logo_id = request.POST.get('logo_id')
            logo_obj = get_object_or_404(NavbarImage, pk=logo_id, image_type='logo')
            
            if logo_obj.is_active:
                # If deactivating, just deactivate this one
                logo_obj.is_active = False
            else:
                # If activating, deactivate all others first, then activate this one
                NavbarImage.objects.filter(image_type='logo', is_active=True).update(is_active=False)
                logo_obj.is_active = True
            
            logo_obj.save()
            log_admin_activity(request.user, 'update', 'NavbarImage', f'Toggled active status for logo: {logo_obj.name}', request, logo_obj.id)
            messages.success(request, f'Logo "{logo_obj.name}" status updated!')
        
        elif action == 'delete':
            logo_id = request.POST.get('logo_id')
            logo_obj = get_object_or_404(NavbarImage, pk=logo_id, image_type='logo')
            logo_name = logo_obj.name
            logo_obj.delete()
            log_admin_activity(request.user, 'delete', 'NavbarImage', f'Deleted logo: {logo_name}', request, logo_id)
            messages.success(request, f'Logo "{logo_name}" deleted successfully!')
        
        elif action == 'edit':
            logo_id = request.POST.get('logo_id')
            logo_obj = get_object_or_404(NavbarImage, pk=logo_id, image_type='logo')
            try:
                logo_obj.name = request.POST.get('name', 'Company Logo')
                logo_obj.order = int(request.POST.get('order', 0))
                logo_obj.is_active = request.POST.get('is_active') == 'on'
                
                # If activating this logo, deactivate others first
                if logo_obj.is_active:
                    NavbarImage.objects.filter(image_type='logo', is_active=True).exclude(pk=logo_obj.pk).update(is_active=False)
                
                # Update image file if provided
                if 'image' in request.FILES:
                    logo_obj.image = request.FILES['image']
                
                logo_obj.save()
                log_admin_activity(request.user, 'update', 'NavbarImage', f'Updated logo: {logo_obj.name}', request, logo_obj.id)
                messages.success(request, f'Logo "{logo_obj.name}" updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating logo: {str(e)}')
        
        return redirect('custom_admin:logo_upload')
    
    log_admin_activity(request.user, 'view', 'NavbarImage', 'Viewed logo upload management', request)
    
    context = {
        'logos': logos,
    }
    return render(request, 'custom_admin/logo_upload.html', context)


@login_required
def carousel_slides(request):
    """Manage carousel slides"""
    slides = CarouselSlide.objects.all().order_by('order', '-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                # Process the uploaded image
                processed_image = resize_image(request.FILES['image'], target_width=1200, target_height=650)
                
                slide_obj = CarouselSlide.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    image=processed_image,
                    button_text=request.POST.get('button_text', 'More Details'),
                    button_url=request.POST.get('button_url'),
                    is_active=request.POST.get('is_active') == 'on',
                    order=int(request.POST.get('order', 0)),
                )
                log_admin_activity(request.user, 'create', 'CarouselSlide', f'Created carousel slide: {slide_obj.title}', request, slide_obj.id)
                messages.success(request, f'Carousel slide "{slide_obj.title}" created successfully! Image resized to 1200x650.')
            except Exception as e:
                messages.error(request, f'Error creating carousel slide: {str(e)}')
        
        elif action == 'toggle_active':
            slide_id = request.POST.get('slide_id')
            slide_obj = get_object_or_404(CarouselSlide, pk=slide_id)
            slide_obj.is_active = not slide_obj.is_active
            slide_obj.save()
            log_admin_activity(request.user, 'update', 'CarouselSlide', f'Toggled active status for: {slide_obj.title}', request, slide_obj.id)
            messages.success(request, f'Slide "{slide_obj.title}" status updated!')
        
        elif action == 'delete':
            slide_id = request.POST.get('slide_id')
            slide_obj = get_object_or_404(CarouselSlide, pk=slide_id)
            slide_title = slide_obj.title
            slide_obj.delete()
            log_admin_activity(request.user, 'delete', 'CarouselSlide', f'Deleted carousel slide: {slide_title}', request, slide_id)
            messages.success(request, f'Slide "{slide_title}" deleted successfully!')
        
        elif action == 'update':
            slide_id = request.POST.get('slide_id')
            slide_obj = get_object_or_404(CarouselSlide, pk=slide_id)
            try:
                slide_obj.title = request.POST.get('title')
                slide_obj.description = request.POST.get('description')
                slide_obj.button_text = request.POST.get('button_text', 'More Details')
                slide_obj.button_url = request.POST.get('button_url')
                slide_obj.is_active = request.POST.get('is_active') == 'on'
                slide_obj.order = int(request.POST.get('order', 0))
                
                if 'image' in request.FILES:
                    # Delete old image file
                    if slide_obj.image:
                        delete_image_file(slide_obj.image.path)
                    
                    # Process new image
                    processed_image = resize_image(request.FILES['image'], target_width=1200, target_height=650)
                    slide_obj.image = processed_image
                
                slide_obj.save()
                log_admin_activity(request.user, 'update', 'CarouselSlide', f'Updated carousel slide: {slide_obj.title}', request, slide_obj.id)
                messages.success(request, f'Slide "{slide_obj.title}" updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating slide: {str(e)}')
        
        return redirect('custom_admin:carousel_slides')
    
    log_admin_activity(request.user, 'view', 'CarouselSlide', 'Viewed carousel slides management', request)
    
    context = {
        'slides': slides,
    }
    return render(request, 'custom_admin/carousel_slides.html', context)


@login_required
def land_properties(request):
    """Manage land properties"""
    land_properties_list = LandProperty.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        land_properties_list = land_properties_list.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search) |
            Q(district__icontains=search) |
            Q(area_name__icontains=search)
        )
    
    # Filter functionality
    status_filter = request.GET.get('status', '')
    if status_filter:
        land_properties_list = land_properties_list.filter(project_status=status_filter)
    
    type_filter = request.GET.get('type', '')
    if type_filter:
        land_properties_list = land_properties_list.filter(property_type=type_filter)
    
    division_filter = request.GET.get('division', '')
    if division_filter:
        land_properties_list = land_properties_list.filter(division=division_filter)
    
    district_filter = request.GET.get('district', '')
    if district_filter:
        land_properties_list = land_properties_list.filter(district__icontains=district_filter)
    
    upazila_filter = request.GET.get('upazila', '')
    if upazila_filter:
        land_properties_list = land_properties_list.filter(area_name__icontains=upazila_filter)
    
    paginator = Paginator(land_properties_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                land_property = LandProperty.objects.create(
                    name=request.POST.get('name'),
                    area=request.POST.get('area'),
                    location=request.POST.get('location'),
                    division=request.POST.get('division'),
                    district=request.POST.get('district'),
                    area_name=request.POST.get('area_name'),
                    description=request.POST.get('description'),
                    project_status=request.POST.get('project_status'),
                    property_type=request.POST.get('property_type'),
                    price_per_katha=request.POST.get('price_per_katha') or None,
                    total_plots=int(request.POST.get('total_plots', 0)) or None,
                    available_plots=int(request.POST.get('available_plots', 0)) or None,
                    amenities=request.POST.get('amenities'),
                    is_featured=request.POST.get('is_featured') == 'on',
                    is_active=request.POST.get('is_active') == 'on',
                )
                if 'image' in request.FILES:
                    land_property.image = request.FILES['image']
                    land_property.save()
                
                log_admin_activity(request.user, 'create', 'LandProperty', f'Created land property: {land_property.name}', request, land_property.id)
                messages.success(request, f'Land property "{land_property.name}" created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating land property: {str(e)}')
        
        elif action == 'update':
            land_property_id = request.POST.get('land_property_id')
            land_property = get_object_or_404(LandProperty, pk=land_property_id)
            try:
                land_property.name = request.POST.get('name')
                land_property.area = request.POST.get('area')
                land_property.location = request.POST.get('location')
                land_property.division = request.POST.get('division')
                land_property.district = request.POST.get('district')
                land_property.area_name = request.POST.get('area_name')
                land_property.description = request.POST.get('description')
                land_property.project_status = request.POST.get('project_status')
                land_property.property_type = request.POST.get('property_type')
                land_property.price_per_katha = request.POST.get('price_per_katha') or None
                land_property.total_plots = int(request.POST.get('total_plots', 0)) or None
                land_property.available_plots = int(request.POST.get('available_plots', 0)) or None
                land_property.amenities = request.POST.get('amenities')
                land_property.is_featured = request.POST.get('is_featured') == 'on'
                land_property.is_active = request.POST.get('is_active') == 'on'
                
                if 'image' in request.FILES:
                    land_property.image = request.FILES['image']
                
                land_property.save()
                log_admin_activity(request.user, 'update', 'LandProperty', f'Updated land property: {land_property.name}', request, land_property.id)
                messages.success(request, f'Land property "{land_property.name}" updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating land property: {str(e)}')
        
        elif action == 'delete':
            land_property_id = request.POST.get('land_property_id')
            land_property = get_object_or_404(LandProperty, pk=land_property_id)
            land_property_name = land_property.name
            land_property.delete()
            log_admin_activity(request.user, 'delete', 'LandProperty', f'Deleted land property: {land_property_name}', request, land_property_id)
            messages.success(request, f'Land property "{land_property_name}" deleted successfully!')
        
        elif action == 'toggle_featured':
            land_property_id = request.POST.get('land_property_id')
            land_property = get_object_or_404(LandProperty, pk=land_property_id)
            land_property.is_featured = not land_property.is_featured
            land_property.save()
            log_admin_activity(request.user, 'update', 'LandProperty', f'Toggled featured status for: {land_property.name}', request, land_property.id)
            messages.success(request, f'Land property "{land_property.name}" featured status updated!')
        
        elif action == 'toggle_active':
            land_property_id = request.POST.get('land_property_id')
            land_property = get_object_or_404(LandProperty, pk=land_property_id)
            land_property.is_active = not land_property.is_active
            land_property.save()
            log_admin_activity(request.user, 'update', 'LandProperty', f'Toggled active status for: {land_property.name}', request, land_property.id)
            messages.success(request, f'Land property "{land_property.name}" active status updated!')
        
        return redirect('custom_admin:land_properties')
    
    log_admin_activity(request.user, 'view', 'LandProperty', 'Viewed land properties management', request)
    
    # Get unique districts and upazilas for filter dropdowns
    districts = LandProperty.objects.values_list('district', flat=True).distinct().order_by('district')
    upazilas = LandProperty.objects.values_list('area_name', flat=True).distinct().order_by('area_name')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'division_filter': division_filter,
        'district_filter': district_filter,
        'upazila_filter': upazila_filter,
        'project_statuses': LandProperty.PROJECT_STATUS,
        'property_types': LandProperty.PROPERTY_TYPE,
        'divisions': LandProperty.DIVISIONS,
        'districts': districts,
        'upazilas': upazilas,
    }
    return render(request, 'custom_admin/land_properties.html', context)


@login_required
def activities(request):
    """View admin activities with dynamic features"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    # Base queryset with related data
    activities = AdminActivity.objects.select_related('admin').order_by('-timestamp')
    
    # Filter by admin if specified
    admin_filter = request.GET.get('admin', '')
    if admin_filter:
        activities = activities.filter(admin__username__icontains=admin_filter)
    
    # Filter by action if specified
    action_filter = request.GET.get('action', '')
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    # Filter by model if specified
    model_filter = request.GET.get('model', '')
    if model_filter:
        activities = activities.filter(model_name=model_filter)
    
    # Filter by date range if specified
    date_filter = request.GET.get('date_range', '')
    if date_filter:
        now = timezone.now()
        if date_filter == 'today':
            activities = activities.filter(timestamp__date=now.date())
        elif date_filter == 'week':
            week_ago = now - timedelta(days=7)
            activities = activities.filter(timestamp__gte=week_ago)
        elif date_filter == 'month':
            month_ago = now - timedelta(days=30)
            activities = activities.filter(timestamp__gte=month_ago)
        elif date_filter == 'year':
            year_ago = now - timedelta(days=365)
            activities = activities.filter(timestamp__gte=year_ago)
    
    # Handle export request
    if request.GET.get('export'):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="admin_activities_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Admin', 'Action', 'Model', 'Description', 'IP Address', 'Timestamp', 'Object ID'])
        
        for activity in activities:
            writer.writerow([
                activity.admin.username,
                activity.get_action_display(),
                activity.model_name,
                activity.description,
                activity.ip_address,
                activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                activity.object_id or ''
            ])
        
        return response
    
    # Calculate comprehensive statistics
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Basic counts
    total_activities = AdminActivity.objects.count()
    today_activities = AdminActivity.objects.filter(timestamp__date=today).count()
    week_activities = AdminActivity.objects.filter(timestamp__gte=week_ago).count()
    month_activities = AdminActivity.objects.filter(timestamp__gte=month_ago).count()
    
    # Active admins (logged in within last 7 days)
    active_admins = AdminActivity.objects.filter(
        timestamp__gte=week_ago,
        action='login'
    ).values('admin').distinct().count()
    
    # Recent changes (create, update, delete in last 7 days)
    recent_changes = AdminActivity.objects.filter(
        action__in=['create', 'update', 'delete'],
        timestamp__gte=week_ago
    ).count()
    
    
    # Get unique model types and admin users for filters
    model_types = AdminActivity.objects.values_list('model_name', flat=True).distinct().order_by('model_name')
    admin_users = AdminActivity.objects.values_list('admin__username', flat=True).distinct().order_by('admin__username')
    
    # Pagination
    paginator = Paginator(activities, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Log this activity
    log_admin_activity(request.user, 'view', 'AdminActivity', f'Viewed admin activities (page {page_number or 1})', request)
    
    context = {
        'page_obj': page_obj,
        'admin_filter': admin_filter,
        'action_filter': action_filter,
        'model_filter': model_filter,
        'date_filter': date_filter,
        'action_types': AdminActivity.ACTION_TYPES,
        'model_types': model_types,
        'admin_users': admin_users,
        'total_activities': total_activities,
        'today_activities': today_activities,
        'week_activities': week_activities,
        'month_activities': month_activities,
        'active_admins': active_admins,
        'recent_changes': recent_changes,
    }
    return render(request, 'custom_admin/activities.html', context)


@login_required
def delete_all_activities(request):
    """Delete all admin activities"""
    if request.method == 'POST':
        # Get count before deletion for logging
        total_count = AdminActivity.objects.count()
        
        # Delete all activities
        AdminActivity.objects.all().delete()
        
        # Log this activity
        log_admin_activity(request.user, 'delete', 'AdminActivity', f'Deleted all {total_count} admin activities', request)
        
        messages.success(request, f'Successfully deleted all {total_count} admin activities.')
        return redirect('custom_admin:activities')
    
    # If GET request, show confirmation page
    total_activities = AdminActivity.objects.count()
    context = {
        'total_activities': total_activities,
    }
    return render(request, 'custom_admin/delete_all_activities.html', context)


@login_required
def admin_profile(request):
    """Admin profile management"""
    # Get or create admin profile
    profile, created = AdminProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            try:
                # Update user basic info
                request.user.first_name = request.POST.get('first_name', '')
                request.user.last_name = request.POST.get('last_name', '')
                request.user.email = request.POST.get('email', '')
                request.user.save()
                
                # Update profile info
                profile.phone = request.POST.get('phone', '')
                
                # Update profile image if provided
                if 'profile_image' in request.FILES:
                    profile.profile_image = request.FILES['profile_image']
                
                profile.save()
                
                log_admin_activity(request.user, 'update', 'AdminProfile', 'Updated admin profile information', request)
                messages.success(request, 'Profile updated successfully!')
                
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        
        elif action == 'change_password':
            try:
                current_password = request.POST.get('current_password')
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                # Validate current password
                if not check_password(current_password, request.user.password):
                    messages.error(request, 'Current password is incorrect.')
                    return redirect('custom_admin:admin_profile')
                
                # Validate new password
                if new_password != confirm_password:
                    messages.error(request, 'New passwords do not match.')
                    return redirect('custom_admin:admin_profile')
                
                if len(new_password) < 8:
                    messages.error(request, 'New password must be at least 8 characters long.')
                    return redirect('custom_admin:admin_profile')
                
                # Update password
                request.user.password = make_password(new_password)
                request.user.save()
                
                log_admin_activity(request.user, 'update', 'AdminProfile', 'Changed admin password', request)
                messages.success(request, 'Password changed successfully!')
                
            except Exception as e:
                messages.error(request, f'Error changing password: {str(e)}')
        
        return redirect('custom_admin:admin_profile')
    
    # Get admin statistics
    admin_stats = {
        'total_activities': AdminActivity.objects.filter(admin=request.user).count(),
        'today_activities': AdminActivity.objects.filter(
            admin=request.user, 
            timestamp__date=timezone.now().date()
        ).count(),
        'last_login': AdminActivity.objects.filter(
            admin=request.user, 
            action='login'
        ).order_by('-timestamp').first(),
        'profile_created': profile.created_at,
        'last_updated': profile.updated_at,
    }
    
    # Get recent activities for this admin
    recent_activities = AdminActivity.objects.filter(admin=request.user).order_by('-timestamp')[:10]
    
    log_admin_activity(request.user, 'view', 'AdminProfile', 'Viewed admin profile page', request)
    
    context = {
        'profile': profile,
        'admin_stats': admin_stats,
        'recent_activities': recent_activities,
    }
    return render(request, 'custom_admin/admin_profile.html', context)


@login_required
def contact_messages(request):
    """Manage contact messages"""
    contact_messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        contact_messages_list = contact_messages_list.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(message__icontains=search)
        )
    
    # Filter functionality
    status_filter = request.GET.get('status', '')
    if status_filter:
        contact_messages_list = contact_messages_list.filter(status=status_filter)
    
    property_type_filter = request.GET.get('property_type', '')
    if property_type_filter:
        contact_messages_list = contact_messages_list.filter(property_type=property_type_filter)
    
    budget_filter = request.GET.get('budget', '')
    if budget_filter:
        contact_messages_list = contact_messages_list.filter(budget=budget_filter)
    
    # Pagination
    paginator = Paginator(contact_messages_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            message_id = request.POST.get('message_id')
            new_status = request.POST.get('status')
            message_obj = get_object_or_404(ContactMessage, pk=message_id)
            old_status = message_obj.status
            message_obj.status = new_status
            message_obj.save()
            
            log_admin_activity(request.user, 'update', 'ContactMessage', f'Updated message status from {old_status} to {new_status} for {message_obj.full_name}', request, message_obj.id)
            messages.success(request, f'Message status updated to {message_obj.get_status_display()}!')
        
        elif action == 'delete':
            message_id = request.POST.get('message_id')
            message_obj = get_object_or_404(ContactMessage, pk=message_id)
            message_name = message_obj.full_name
            message_obj.delete()
            
            log_admin_activity(request.user, 'delete', 'ContactMessage', f'Deleted contact message from {message_name}', request, message_id)
            messages.success(request, f'Message from {message_name} deleted successfully!')
        
        elif action == 'mark_all_read':
            updated_count = ContactMessage.objects.filter(status='new').update(status='read')
            log_admin_activity(request.user, 'update', 'ContactMessage', f'Marked {updated_count} messages as read', request)
            messages.success(request, f'{updated_count} messages marked as read!')
        
        return redirect('custom_admin:contact_messages')
    
    log_admin_activity(request.user, 'view', 'ContactMessage', 'Viewed contact messages management', request)
    
    # Get statistics
    stats = {
        'total_messages': ContactMessage.objects.count(),
        'new_messages': ContactMessage.objects.filter(status='new').count(),
        'read_messages': ContactMessage.objects.filter(status='read').count(),
        'replied_messages': ContactMessage.objects.filter(status='replied').count(),
        'closed_messages': ContactMessage.objects.filter(status='closed').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'property_type_filter': property_type_filter,
        'budget_filter': budget_filter,
        'stats': stats,
        'status_choices': ContactMessage.STATUS_CHOICES,
        'property_interest_choices': ContactMessage.PROPERTY_INTEREST_CHOICES,
        'budget_choices': ContactMessage.BUDGET_CHOICES,
    }
    return render(request, 'custom_admin/contact_messages.html', context)
