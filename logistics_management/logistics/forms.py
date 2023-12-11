from django import forms
from .models import CargoOrder, Driver, Truck


class AddCargoOrderForm(forms.ModelForm):
    class Meta:
        model = CargoOrder
        exclude = ['status']

class EditCargoOrderForm(forms.ModelForm):
    class Meta:
        model = CargoOrder
        fields = ['truck', 'start_point', 'load', 'destination', 'status']
        

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['license_number', 'first_name', 'last_name']
        

class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        fields = ['driver', 'license_plate', 'capacity']