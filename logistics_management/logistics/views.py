from django.shortcuts import render
from .models import CargoOrder

def logistics_list(request):
    
    cargo_list = CargoOrder.objects.all()
    
    return render(request, "logistics/logistics_list.html", {"cargo_list": cargo_list})