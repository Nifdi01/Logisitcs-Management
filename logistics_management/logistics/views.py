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
    path_coordinates = [coordinates[point] for point in shortest_path]
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
        "path_coordinates": path_coordinates,
        "start_lat": coordinates[shortest_path[0]][0],
        "start_long": coordinates[shortest_path[0]][1],
        "end_lat": coordinates[shortest_path[-1]][0],
        "end_long": coordinates[shortest_path[-1]][1],
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
    "Aghdam": {"Tartar": 49.5, "Aghdara": 36.4, "Barda": 47.3, "Aghjabadi": 47.9, "Khojavend": 32.8},    
    "Agdash": {"Shaki": 85.8, "Qabala": 57.2, "Goychay": 27.6, "Ujar": 34.5, "Zardab": 66.5, "Barda": 63.4, "Yevlakh": 38.6, "Mingachevir": 40.5},    
    "Aghjabadi": {"Aghdam": 47.9, "Barda": 52.6, "Zardab": 37.5, "Beylagan": 47.1, "Fuzuli": 112.0},    
    "Aghstafa": {"Qazakh": 11.4, "Tovuz": 21.8},    
    "Aghsu": {"Ismayilli": 66.6, "Shamakhi": 43.7, "Hajigabul": 104.7, "Kurdamir": 27.4, "Goychay": 64.7},    
    "Astara": {"Lankaran": 38.6},    
    "Aghdara": {"Aghdam": 33.3, "Tartar": 40.1},    
    "Babek": {"Julfa": 31.4, "Nakhchivan": 9.3, "Sharur": 69.2},    
    "Baku": {"Sumgayit": 30.5, "Khirdalan": 15.6, "Shirvan": 130.9, "Hajigabul": 120.0},    
    "Balakan": {"Zaqatala": 29.3},    
    "Barda": {"Yevlakh": 30.3, "Agdash": 63.4, "Aghjabadi": 52.6, "Aghdam": 47.3, "Tartar": 20.4},    
    "Beylagan": {"Fuzuli": 71.8, "Aghjabadi": 47.1, "Imishli": 60.7},    
    "Bilasuvar": {"Imishli": 80.4, "Saatli": 89.3, "Sabirabad": 82.1},    
    "Dashkasan": {"Shamkir": 68.9, "Ganja": 41.0, "Goygol": 41.4, "Kalbajar": 139.9},    
    "Shabran": {"Khachmaz": 37.2, "Quba": 47.0, "Siyazan": 20.8},    
    "Fuzuli": {"Jabrayil": 33.8, "Khojavend": 26.8, "Aghjabadi": 112.0, "Beylagan": 71.8},    
    "Gadabay": {"Tovuz": 82.1, "Shamkir": 45.4},    
    "Ganja": {"Shamkir": 39.9, "Dashkasan": 41.0, "Goygol": 13.3, "Goranboy": 43.0},    
    "Goranboy": {"Ganja": 43.0, "Goygol": 52.6, "Naftalan": 17.6, "Yevlakh": 36.4},    
    "Goychay": {"Agdash": 27.6, "Ismayilli": 52.0, "Aghsu": 64.7, "Kurdamir": 64.2, "Ujar": 19.2},    
    "Goygol": {"Dashkasan": 41.4, "Ganja": 13.3, "Goranboy": 52.6, "Naftalan": 66.6, "Kalbajar": 97.6},    
    "Hajigabul": {"Baku": 120.0, "Shamakhi": 94.8, "Aghsu": 104.7, "Kurdamir": 79.3, "Sabirabad": 56.8, "Shirvan": 15.8},    
    "Imishli": {"Beylagan": 60.7, "Zardab": 83.9, "Kurdamir": 66.3, "Sabirabad": 40.7, "Saatli": 32.5, "Bilasuvar": 80.4},    
    "Ismayilli": {"Qabala": 44.4, "Shamakhi": 54.6, "Aghsu": 66.6, "Goychay": 52.0, "Shirvan": 164.1},    
    "Jabrayil": {"Zangilan": 81.2, "Qubadli": 58.0, "Fuzuli": 33.8},    
    "Julfa": {"Ordubad": 39.4, "Nakhchivan": 35.7, "Babek": 31.4},    
    "Kalbajar":{"Dashkasan": 139.9, "Goygol": 97.6, "Khankendi": 120.9},    
    "Khachmaz": {"Quba": 27.6, "Shabran": 37.2},    
    "Khankendi": {"Shusha": 14.3, "Khojavend": 41.2, "Kalbajar": 120.9},    
    "Khojavend": {"Aghdam": 32.8, "Fuzuli": 26.8, "Khankendi": 41.2},    
    "Khirdalan": {"Sumgayit": 20.2, "Baku": 15.6},    
    "Kurdamir": {"Ujar": 53.6, "Goychay": 64.2, "Aghsu": 27.4, "Hajigabul": 79.3, "Sabirabad": 71.4, "Imishli": 66.3, "Zardab": 64.2},    
    "Lankaran": {"Astara": 38.6, "Lerik": 52.3, "Masally": 39.2, "Neftchala": 161.0},    
    "Lerik": {"Yardimli": 42.3, "Masally": 53.0, "Lankaran": 52.3},    
    "Masally": {"Neftchala": 126.2, "Lankaran": 39.2, "Lerik": 53.0, "Yardimli": 55.6},    
    "Mingachevir": {"Shaki": 74.0, "Agdash": 40.5, "Yevlakh": 32.6},    
    "Nakhchivan": {"Babek": 9.3, "Shahbuz": 32.0, "Julfa": 35.7, "Sharur": 62.9},    
    "Naftalan": {"Goygol": 66.6, "Goranboy": 17.6},    
    "Neftchala": {"Masally": 126.2, "Lankaran": 161.0},    
    "Oghuz": {"Shaki": 41.9, "Qabala": 53.9},    
    "Ordubad": {"Julfa": 39.4},    
    "Qabala": {"Shaki": 88.1, "Oghuz": 53.9, "Ismayilli": 44.4, "Agdash": 57.2},    
    "Qakh": {"Zaqatala": 34.1, "Shaki": 38.6},    
    "Qazakh": {"Aghstafa": 11.4},    
    "Quba": {"Qusar": 13.9, "Khachmaz": 27.6, "Shabran": 47.0},    
    "Qubadli": {"Jabrayil": 58.0, "Zangilan": 56.2},    
    "Qusar": {"Quba": 13.9},    
    "Saatli": {"Imishli": 32.5, "Sabirabad": 16.4, "Bilasuvar": 89.3},    
    "Sabirabad": {"Kurdamir": 71.4, "Hajigabul": 56.8, "Shirvan": 46.6, "Bilasuvar": 82.1, "Saatli": 16.4, "Imishli": 40.7},    
    "Shahbuz": {"Nakhchivan": 32.0},    
    "Shaki": {"Qakh": 38.6, "Oghuz": 41.9, "Agdash": 85.8, "Mingachevir": 74.0, "Qabala": 88.1},
    "Shamakhi": {"Hajigabul": 94.8, "Aghsu": 43.7, "Ismayilli": 54.6},    
    "Shamkir": {"Tovuz": 46.6, "Ganja": 39.9, "Dashkasan": 68.9, "Gadabay": 45.4},    
    "Sharur": {"Babek": 69.2, "Nakhchivan": 62.9},    
    "Shirvan": {"Hajigabul": 15.8, "Sabirabad": 46.6, "Baku": 130.9, "Ismayilli": 164.1},    
    "Siyazan": {"Shabran": 20.8},    
    "Shusha": {"Khankendi": 14.3},    
    "Sumgayit": {"Baku": 30.5, "Khirdalan": 20.2},    
    "Tartar": {"Aghdara": 36.4, "Aghdam": 49.5, "Barda": 20.4},    
    "Tovuz": {"Aghstafa": 21.8, "Shamkir": 46.6, "Gadabay": 82.6},    
    "Ujar": {"Agdash": 34.5, "Goychay": 19.2, "Kurdamir": 53.6, "Zardab": 36.7},    
    "Yardimli": {"Masally": 55.6, "Lerik": 42.3},    
    "Yevlakh": {"Mingachevir": 32.6, "Agdash": 38.6, "Barda": 30.3, "Goranboy": 36.4},    
    "Zaqatala": {"Balakan": 29.3, "Qakh": 34.1},    
    "Zardab": {"Agdash": 66.5, "Ujar": 36.7, "Kurdamir": 64.2, "Imishli": 83.9, "Aghjabadi": 37.5},    
    "Zangilan": {"Qubadli": 56.2, "Jabrayil": 81.2}    
}

coordinates = {
    "Aghdam": (39.9910, 46.9274), 
    "Agdash": (40.6470, 47.4738), 
    "Aghjabadi": (40.0501, 47.4594),
    "Aghstafa": (41.1189, 45.4539),
    "Aghsu": (40.5703, 48.4009),
    "Astara": (38.4560, 48.8750),
    "Aghdara": (40.2153, 46.8128),
    "Babek": (39.1508, 45.4485),
    "Baku": (40.3777, 49.8920),
    "Balakan": (41.7263, 46.4048),
    "Barda": (40.3758, 47.1262),
    "Beylagan": (39.7756, 47.6186),
    "Bilasuvar": (39.4599, 48.5510),
    "Dashkasan": (40.5202, 46.0779),
    "Shabran": (41.2160, 48.9946),
    "Fuzuli": (39.6009, 47.1453),
    "Gadabay": (40.5700, 45.8107),
    "Ganja": (40.6828, 46.3606),
    "Goranboy": (40.6103, 46.7897),
    "Goychay": (40.6236, 47.7403),
    "Goygol": (40.5858, 46.3189),
    "Hajigabul": (40.0387, 48.9429),
    "Imishli": (39.8710, 48.0600),
    "Ismayilli": (40.7849, 48.1514),
    "Jabrayil": (39.3987, 47.0245),
    "Julfa": (38.9558, 45.6308),
    "Kalbajar": (40.1024, 46.0365),
    "Khachmaz": (41.4591, 48.8021),
    "Khankendi": (39.8265, 46.7656),
    "Khojavend": (39.7915, 47.1101),
    "Khirdalan": (40.4481, 49.7550),
    "Kurdamir": (40.3453, 48.1509),
    "Lankaran": (38.7543, 48.8506),
    "Lerik": (38.7739, 48.4150),
    "Masally": (39.0353, 48.6654),
    "Mingachevir": (40.7640, 47.0595),
    "Nakhchivan": (39.2089, 45.4122),
    "Naftalan": (40.5082, 46.8203),
    "Neftchala": (39.3768, 49.2470),
    "Oghuz": (41.0713, 47.4653),
    "Ordubad": (38.9060, 46.0234),
    "Qabala": (40.9982, 47.8700),
    "Qakh": (41.4183, 46.9204),
    "Qazakh": (41.0925, 45.3656),
    "Quba": (41.3611, 48.5134),
    "Qubadli": (39.3444, 46.5818),
    "Qusar": (41.4275, 48.4302),
    "Saatli": (39.9321, 48.3689),
    "Sabirabad": (40.0087, 48.4770),
    "Shahbuz": (39.4072, 45.5739),
    "Shaki": (41.1975, 47.1571),
    "Shamakhi": (40.6314, 48.6414),
    "Shamkir": (40.8298, 46.0178),
    "Sharur": (39.5536, 44.9846),
    "Shirvan": (39.9378, 48.9290),
    "Siyazan": (41.0784, 49.1118),
    "Shusha": (39.7561, 46.7460),
    "Sumgayit": (40.5897, 49.6686),
    "Tartar": (40.3418, 46.9324),
    "Tovuz": (40.9925, 45.6284),
    "Ujar": (40.5190, 47.6542),
    "Yardimli": (38.9077, 48.2405),
    "Yevlakh": (40.6183, 47.1501),
    "Zaqatala": (41.6316, 46.6448),
    "Zardab": (40.2199, 47.7100),
    "Zangilan": (39.0884, 46.6513) 
}