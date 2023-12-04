from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.logistics_list, name="logistics_list"),
    path('cargo/<int:pk>', views.logistics_detail, name="logistics_detail"),
]
