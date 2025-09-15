from django.contrib import admin
from .models import CompanyInfo, NavbarImage, CarouselSlide, LandProperty, ContactMessage


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']


@admin.register(NavbarImage)
class NavbarImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_type', 'is_active', 'order', 'created_at']
    list_filter = ['image_type', 'is_active']
    list_editable = ['is_active', 'order']
    search_fields = ['name']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('name', 'image_type', 'image')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order'),
            'description': 'Only one image per type can be active at a time'
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', '-created_at')


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'slide_type', 'is_active', 'order', 'created_at']
    list_filter = ['slide_type', 'is_active', 'created_at']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'subtitle', 'description']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Slide Content', {
            'fields': ('title', 'subtitle', 'description', 'slide_type')
        }),
        ('Visual Settings', {
            'fields': ('image', 'background_color')
        }),
        ('Action Button', {
            'fields': ('button_text', 'button_url')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(LandProperty)
class LandPropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'division', 'district', 'project_status', 'property_type', 'is_featured', 'is_active', 'created_at']
    list_filter = ['project_status', 'property_type', 'division', 'is_featured', 'is_active', 'created_at']
    list_editable = ['is_featured', 'is_active']
    search_fields = ['name', 'location', 'district', 'area_name', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'description', 'area', 'location'),
            'description': 'Basic information about the land property project'
        }),
        ('Location Details', {
            'fields': ('division', 'district', 'area_name'),
            'description': 'Select the administrative division, district, and upazila'
        }),
        ('Project Details', {
            'fields': ('project_status', 'property_type', 'price_per_katha', 'total_plots', 'available_plots'),
            'description': 'Project status, type, pricing, and plot information'
        }),
        ('Additional Information', {
            'fields': ('amenities',),
            'description': 'List of amenities and facilities available'
        }),
        ('Status & Display', {
            'fields': ('is_featured', 'is_active'),
            'description': 'Control visibility and featured status'
        }),
        ('Images', {
            'fields': ('image',),
            'description': 'Upload project image (recommended size: 800x600px)'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text to form fields
        form.base_fields['division'].help_text = 'Select the administrative division'
        form.base_fields['district'].help_text = 'Enter the district name'
        form.base_fields['area_name'].help_text = 'Enter the upazila/thana name'
        form.base_fields['project_status'].help_text = 'Current status of the project'
        form.base_fields['property_type'].help_text = 'Type of property development'
        form.base_fields['price_per_katha'].help_text = 'Price per katha in BDT (optional)'
        form.base_fields['total_plots'].help_text = 'Total number of plots in the project (optional)'
        form.base_fields['available_plots'].help_text = 'Number of plots still available (optional)'
        form.base_fields['amenities'].help_text = 'List amenities separated by commas (e.g., Road, Electricity, Water, Security)'
        return form


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'property_type', 'status', 'created_at']
    list_filter = ['status', 'property_type', 'budget', 'newsletter_subscription', 'created_at']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'message']
    readonly_fields = ['created_at', 'updated_at', 'ip_address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Property Interest', {
            'fields': ('property_type', 'budget')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Preferences', {
            'fields': ('newsletter_subscription',)
        }),
        ('Status & Tracking', {
            'fields': ('status', 'ip_address', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')