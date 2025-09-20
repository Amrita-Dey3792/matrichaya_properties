from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .image_utils import delete_image_file


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, default="Matrichaya Properties Ltd.")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    about_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Company Information"


class NavbarImage(models.Model):
    IMAGE_TYPES = [
        ('logo', 'Logo'),
        ('banner', 'Banner'),
        ('background', 'Background'),
    ]
    
    name = models.CharField(max_length=100, help_text="Name/description of the image")
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default='logo')
    image = models.ImageField(upload_to='navbar/', help_text="Upload navbar image")
    is_active = models.BooleanField(default=True, help_text="Whether this image is currently active")
    order = models.PositiveIntegerField(default=0, help_text="Order of display (lower numbers first)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Navbar Image"
        verbose_name_plural = "Navbar Images"
    
    def __str__(self):
        return f"{self.name} ({self.get_image_type_display()})"
    
    def save(self, *args, **kwargs):
        # If this image is being set as active, deactivate others of the same type
        if self.is_active:
            NavbarImage.objects.filter(
                image_type=self.image_type, 
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class CarouselSlide(models.Model):
    title = models.CharField(max_length=200, help_text="Main title of the slide")
    description = models.TextField(help_text="Detailed description")
    image = models.ImageField(upload_to='carousel/', help_text="Slide background image")
    button_text = models.CharField(max_length=50, default="More Details", help_text="Button text")
    button_url = models.URLField(blank=True, help_text="Button link URL")
    is_active = models.BooleanField(default=True, help_text="Whether this slide is currently active")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Carousel Slide"
        verbose_name_plural = "Carousel Slides"
    
    def __str__(self):
        return f"{self.title} (Order: {self.order})"
    
    def save(self, *args, **kwargs):
        # Ensure only active slides are displayed
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=CarouselSlide)
def delete_carousel_slide_image(sender, instance, **kwargs):
    """Delete the image file when a CarouselSlide is deleted"""
    if instance.image:
        delete_image_file(instance.image.path)


class LandProperty(models.Model):
    PROJECT_STATUS = [
        ('ongoing', 'On Going'),
        ('completed', 'Completed'),
        ('upcoming', 'Up Coming'),
    ]
    
    PROPERTY_TYPE = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed', 'Mixed Use'),
    ]
    
    DIVISIONS = [
        ('dhaka', 'Dhaka'),
        ('chittagong', 'Chittagong'),
        ('rajshahi', 'Rajshahi'),
        ('khulna', 'Khulna'),
        ('barisal', 'Barisal'),
        ('sylhet', 'Sylhet'),
        ('rangpur', 'Rangpur'),
        ('mymensingh', 'Mymensingh'),
    ]
    
    name = models.CharField(max_length=200, help_text="Project name")
    area = models.CharField(max_length=100, help_text="Area in katha/bigha")
    location = models.CharField(max_length=300, help_text="Full location address")
    division = models.CharField(max_length=20, choices=DIVISIONS, default='dhaka')
    district = models.CharField(max_length=100, help_text="District name")
    area_name = models.CharField(max_length=100, help_text="Specific area/upazila")
    description = models.TextField(help_text="Project description")
    image = models.ImageField(upload_to='land_properties/', help_text="Project image")
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='ongoing')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE, default='residential')
    price_per_katha = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Price per katha")
    total_plots = models.PositiveIntegerField(blank=True, null=True, help_text="Total number of plots")
    available_plots = models.PositiveIntegerField(blank=True, null=True, help_text="Available plots")
    amenities = models.TextField(blank=True, help_text="Available amenities")
    is_featured = models.BooleanField(default=False, help_text="Featured project")
    is_active = models.BooleanField(default=True, help_text="Active project")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Land Property"
        verbose_name_plural = "Land Properties"


class ContactMessage(models.Model):
    """Model to store contact form submissions"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    
    PROPERTY_INTEREST_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('land', 'Land Property'),
        ('commercial', 'Commercial Property'),
        ('other', 'Other'),
    ]
    
    BUDGET_CHOICES = [
        ('under-50', 'Under 50 Lakh'),
        ('50-100', '50 Lakh - 1 Crore'),
        ('100-200', '1 Crore - 2 Crore'),
        ('200-500', '2 Crore - 5 Crore'),
        ('above-500', 'Above 5 Crore'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    property_type = models.CharField(max_length=20, choices=PROPERTY_INTEREST_CHOICES, blank=True)
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    message = models.TextField()
    newsletter_subscription = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    def sold_plots(self):
        if self.total_plots and self.available_plots:
            return self.total_plots - self.available_plots
        return 0
    
    @property
    def completion_percentage(self):
        if self.total_plots and self.available_plots:
            return round((self.sold_plots / self.total_plots) * 100, 1)
        return 0