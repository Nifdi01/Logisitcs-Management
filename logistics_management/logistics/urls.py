from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.logistics_list, name="logistics_list"),
    path('cargo/<int:pk>', views.logistics_detail, name="logistics_detail"),
    path('edit_cargo_order/<int:cargo_order_id>/', views.edit_cargo_order, name='edit_cargo_order'),
    path('delete_cargo_order/<int:cargo_order_id>/', views.delete_cargo_order, name='delete_cargo_order'),
    path('add_cargo/', views.add_cargo, name='add_cargo_order'),
    path('add_driver/', views.add_driver, name='add_driver'),
    path('delete_driver/<int:driver_id>/', views.delete_driver, name='delete_driver'),
    path('add_truck/', views.add_truck, name='add_truck'),
    path('delete_truck/<int:truck_id>/', views.delete_truck, name='delete_truck'),
]
