from django.shortcuts import render

def landing_page(request):
    return render(request, "users/landing_page.html")