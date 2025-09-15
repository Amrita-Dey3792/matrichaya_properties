from .models import NavbarImage, CarouselSlide


def navbar_images(request):
    """
    Context processor to make navbar images available in all templates
    """
    return {
        'navbar_images': {
            'logo': NavbarImage.objects.filter(image_type='logo', is_active=True).first(),
            'banner': NavbarImage.objects.filter(image_type='banner', is_active=True).first(),
            'background': NavbarImage.objects.filter(image_type='background', is_active=True).first(),
        },
        'carousel_slides': CarouselSlide.objects.filter(is_active=True).order_by('order', '-created_at')
    }
