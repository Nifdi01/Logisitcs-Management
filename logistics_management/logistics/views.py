from django.shortcuts import render
from .models import *

def sample_view(request):
    
    
    
    return render(request, "logistics/logistics_list.html")