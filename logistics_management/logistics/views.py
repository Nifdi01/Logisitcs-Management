from django.shortcuts import render
from django.http import HttpResponse

def sample_view(request):
    return render(request, "logistics/logistics_list.html")