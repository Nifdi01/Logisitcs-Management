from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.logistics_list, name="logistics_list"),
]
