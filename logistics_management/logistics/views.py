from django.shortcuts import render, get_object_or_404, redirect
from .models import CargoOrder, Driver, Truck
from .forms import AddCargoOrderForm, EditCargoOrderForm, DriverForm, TruckForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q



@login_required
def logistics_list(request):
    # Get the filter parameter from the request's GET parameters
    status_filter = request.GET.get('status', '')

    # Filter cargo orders based on the selected status
    if status_filter:
        cargo_list = CargoOrder.objects.filter(status=status_filter)
        print(status_filter)
    else:
        cargo_list = CargoOrder.objects.all()

    # Set the number of items per page
    items_per_page = 10
    paginator = Paginator(cargo_list, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        cargo_list = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page
        cargo_list = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, deliver the last page of results
        cargo_list = paginator.page(paginator.num_pages)

    return render(request, "logistics/logistics_list.html", {"cargo_list": cargo_list, "status_filter": status_filter})


@login_required
def logistics_detail(request, pk):
    cargo = CargoOrder.objects.get(pk=pk)
    shortest_path = astar(graph, cargo.start_point, cargo.destination, coordinates)
    # shortest_path = ["A", "A", "A", "A", "A", "A", "A", ]
    print(shortest_path)
    hour, minute = calculate_travel_time(int(calculate_cost(shortest_path)))
    time = f"{hour}h {minute}m"
    print(time)
    context = {
        "cargo": cargo,
        "driver": cargo.truck.driver,
        "driver_license": cargo.truck.driver.license_number,
        "truck_plate": cargo.truck,
        "truck_load":cargo.load,
        "start_point": cargo.start_point,
        "destination": cargo.destination,
        "shortest_path": shortest_path[1:-1],
        "total_distance": int(calculate_cost(shortest_path)),
        "travel_time": time,
    }
    
    return render(request, "logistics/logistics_detail.html", context=context)


def edit_cargo_order(request, cargo_order_id):
    cargo_order = get_object_or_404(CargoOrder, id=cargo_order_id)

    if request.method == "POST":
        form = EditCargoOrderForm(request.POST, instance=cargo_order)
        if form.is_valid():
            # Check if the status is changed to 'completed' or 'in queue'
            new_status = form.cleaned_data['status']
            if new_status in [CargoOrder.COMPLETED, CargoOrder.IN_QUEUE]:
                # Get the next order for the same truck
                next_order = CargoOrder.objects.filter(truck=cargo_order.truck, id__gt=cargo_order.id).order_by('id').first()
                if next_order:
                    # Update the status of the next order based on the new status
                    if new_status == CargoOrder.COMPLETED:
                        next_order.status = CargoOrder.IN_PROGRESS
                    elif new_status == CargoOrder.IN_QUEUE:
                        next_order.status = CargoOrder.IN_PROGRESS
                    next_order.save()

            form.save()
            return redirect('logistics_list')
    else:
        form = EditCargoOrderForm(instance=cargo_order)

    return render(request, "logistics/cargo_edit.html", {"form": form})


def add_cargo(request):
    if request.method == "POST":
        form = AddCargoOrderForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            cargo_order = form.save(commit=False)
            
            # Check if the selected truck can hold the specified load
            if cargo_order.truck.capacity >= cargo_order.load:
                existing_orders = CargoOrder.objects.filter(truck=cargo_order.truck).order_by('-id')

                if not existing_orders.exists():
                    # No existing orders, set status to 'in progress'
                    cargo_order.status = CargoOrder.IN_PROGRESS
                else:
                    latest_order_status = existing_orders.first().status

                    if latest_order_status == CargoOrder.COMPLETED:
                        # If the latest order is completed, set status to 'in progress'
                        cargo_order.status = CargoOrder.IN_PROGRESS
                    else:
                        # If there are existing orders, set status to 'in queue'
                        cargo_order.status = CargoOrder.IN_QUEUE
                cargo_order.save()
                messages.success(request, "Cargo order added successfully.")
                return redirect("logistics_list")
            else:
                # Handle the case where the truck's capacity is not sufficient
                error_message = "Selected truck cannot hold the specified load."
                return render(request, "logistics/cargo_add.html", {"form": form, "error_message": error_message})

    else:
        form = AddCargoOrderForm()

    return render(request, "logistics/cargo_add.html", {"form": form})



def delete_cargo_order(request, cargo_order_id):
    cargo_order = get_object_or_404(CargoOrder, id=cargo_order_id)
    if request.method == "POST":
        cargo_order.delete()
        return redirect("logistics_list")
    return render(request, "logistics/cargo_delete.html", {'cargo_order':cargo_order})


def add_driver(request):
    if request.method == "POST":
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("logistics_list")
        
    else:
        form = DriverForm()

    return render(request, "logistics/driver_add.html", {"form":form})


def delete_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == "POST":
        driver.delete()
        return redirect("logistics_list")
    
    return render(request, "logistics/driver_delete.html", {"driver":driver})
    

def add_truck(request):
    if request.method == "POST":
        form = TruckForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("logistics_list")
        
    else:
        form = TruckForm()

    return render(request, "logistics/truck_add.html", {"form":form})


def delete_truck(request, truck_id):
    truck = get_object_or_404(Truck, id=truck_id)
    
    if request.method == "POST":
        truck.delete()
        return redirect("logistics_list")
    
    return render(request, "logistics/truck_delete.html", {"truck":truck})



def calculate_travel_time(distance_km):
    standard_speed_kmh = 80

    time_hours = distance_km / standard_speed_kmh

    hours = int(time_hours)
    minutes = int((time_hours - hours) * 60)

    return hours, minutes



######################
## A star Algorithm ##
######################

import heapq
import math

def heuristic(start_point, destination, coordinates):
    x1, y1 = coordinates[start_point]
    x2, y2 = coordinates[destination]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def astar(graph, start_point, destination, coordinates):
    priority_queue = []
    heapq.heappush(priority_queue, (0, start_point, []))
    visited = set()

    while priority_queue:
        cost, current, path = heapq.heappop(priority_queue)
        print(cost)

        if current in visited:
            continue

        path = path + [current]
        visited.add(current)

        if current == destination:
            return path

        for neighbor, edge_weight in graph[current].items():
            if neighbor not in visited:
                new_cost = cost + edge_weight
                priority = new_cost + heuristic(current, neighbor, coordinates)
                heapq.heappush(priority_queue, (priority, neighbor, path))

    return None


def calculate_cost(shortest_path):
    total_distance = sum(graph[shortest_path[i]][shortest_path[i + 1]] for i in range(len(shortest_path) - 1))
    return total_distance
    

graph = {
    "Baku": {"Khirdalan": 17, "Binagadi": 10, "Lokbatan": 21, "Mardakan": 22, "Mingachevir": 210},
    "Sumgait": {"Khirdalan": 17, "Mardakan": 50},
    "Khirdalan": {"Sumgait": 17, "Baku": 17, "Binagadi": 30},
    "Mardakan": {"Baku": 22, "Sumgait": 50},
    "Lokbatan": {"Baku": 21},
    "Binagadi": {"Khirdalan": 30, "Baku": 10},
    "Mingachevir": {"Ganja": 34, "Baku": 210},
    "Ganja": {"Mingachevir": 34}
}

coordinates = { 
    "Baku": (40.37767, 49.89201),
    "Sumgait": (40.58972, 49.66861),
    "Khirdalan": (40.44808, 49.75502),
    "Mardakan": (40.49182, 50.14292),
    "Lokbatan": (40.3256, 49.73376),
    "Binagadi": (40.46602, 49.82783),
    "Ganja": (40.68278, 46.36056),
    "Mingachevir": (40.76395, 47.05953)
}