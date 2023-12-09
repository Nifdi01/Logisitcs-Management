from django import forms
from .models import CargoOrder, Driver, Truck


class CargoOrderForm(forms.ModelForm):
    class Meta:
        model = CargoOrder
        fields = ['truck', 'start_point', 'destination']
        

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['license_number', 'first_name', 'last_name']
        

class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        fields = ['driver', 'license_plate', 'capacity']