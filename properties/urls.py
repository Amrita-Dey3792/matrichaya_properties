from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('land-properties/', views.land_properties, name='land_properties'),
    path('contact/', views.contact, name='contact'),
    path('contact/ajax/', views.contact_ajax, name='contact_ajax'),
]