from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registration/', views.register, name='register'),
    path('', include('django.contrib.auth.urls')),
]