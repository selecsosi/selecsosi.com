from django.contrib import admin
from .models import Trip, GpsPoint, TripAttr

admin.site.register(Trip)
admin.site.register(GpsPoint)
admin.site.register(TripAttr)
