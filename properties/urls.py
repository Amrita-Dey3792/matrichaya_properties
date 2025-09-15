from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('land-properties/', views.land_properties, name='land_properties'),
    path('land-properties/<int:pk>/', views.land_property_detail, name='land_property_detail'),
    path('contact/', views.contact, name='contact'),
    path('contact/ajax/', views.contact_ajax, name='contact_ajax'),
]