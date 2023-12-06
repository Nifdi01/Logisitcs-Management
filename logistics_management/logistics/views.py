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
        "shortest_path": shortest_path[1:-1],
        "total_distance": int(calculate_cost(shortest_path))
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