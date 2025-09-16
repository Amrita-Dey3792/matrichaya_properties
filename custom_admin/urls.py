from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    
    # Logo Upload
    path('logo-upload/', views.logo_upload, name='logo_upload'),
    
    # Carousel Slides
    path('carousel-slides/', views.carousel_slides, name='carousel_slides'),
    
    # Land Properties
    path('land-properties/', views.land_properties, name='land_properties'),
    
    # Activities
    path('activities/', views.activities, name='activities'),
    path('activities/delete-all/', views.delete_all_activities, name='delete_all_activities'),
    
    # Admin Profile
    path('profile/', views.admin_profile, name='admin_profile'),
]
