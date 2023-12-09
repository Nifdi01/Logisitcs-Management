from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Driver)
admin.site.register(models.Truck)
admin.site.register(models.CargoOrder)
