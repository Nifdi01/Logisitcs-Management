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
    shortest_path = astar(graph, cargo.start_point, cargo.destination, coordinates)
    # shortest_path = ["A", "A", "A", "A", "A", "A", "A", ]
    print(shortest_path)
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

graph = {
    "Baku": {"Khirdalan": 5, "Binagadi": 7, "Lokbatan": 10, "Mardakan": 8, "Mingachevir": 15},
    "Sumgait": {"Khirdalan": 3, "Mardakan": 6},
    "Khirdalan": {"Sumgait": 3, "Baku": 5, "Binagadi": 4},
    "Mardakan": {"Baku": 8, "Sumgait": 9},
    "Lokbatan": {"Baku": 10},
    "Binagadi": {"Khirdalan": 4, "Baku": 7},
    "Mingachevir": {"Ganja": 7, "Baku": 15},
    "Ganja": {"Mingachevir": 7}
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