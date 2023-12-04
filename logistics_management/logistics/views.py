from django.shortcuts import render
from .models import CargoOrder
from django.contrib.auth.decorators import login_required

@login_required
def logistics_list(request):
    cargo_list = CargoOrder.objects.all()
    return render(request, "logistics/logistics_list.html", {"cargo_list": cargo_list})


@login_required
def logistics_detail(request, pk):
    cargo = CargoOrder.objects.get(pk=pk)
    shortest_path = [cargo.start_point, "Agsu", "Bileceri", "Tovuz", "Ceyran Batan", "Bileceri", "Agcabedi", "Nakhcivan","Agsu", "Bileceri", "Tovuz", "Ceyran Batan", "Bileceri", "Agcabedi", "Nakhcivan", cargo.destination]
    context = {
        "cargo": cargo,
        "driver": cargo.truck.driver,
        "driver_license": cargo.truck.driver.license_number,
        "truck_plate": cargo.truck,
        "truck_capacity":cargo.truck.capacity,
        "start_point": cargo.start_point,
        "destination": cargo.destination,
        "shortest_path": shortest_path[1:-1]
    }
    
    return render(request, "logistics/logistics_detail.html", context=context)