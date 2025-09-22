from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    user = models.ForeignKey(User)
    route_csv = models.FileField("Route Data", upload_to='csv/%Y/%m/%d')
    name = models.CharField("Trip Name", max_length=255, blank=True, null=True)
    date = models.DateTimeField("Date", blank=True, null=True)
    created_date = models.DateTimeField("Created Date", editable=False, auto_now_add=True)
    updated_date = models.DateTimeField("Modified Date", editable=False, auto_now=True)

    def __unicode__(self):
        return self.name


class GpsPoint(models.Model):
    trip = models.ForeignKey(Trip, verbose_name="Trip")
    date = models.DateTimeField("Date", blank=True)
    segment = models.IntegerField("Segment")
    point = models.IntegerField("Point")
    lat = models.DecimalField("Latitude", max_digits=16, decimal_places=8)
    lng = models.DecimalField("Longitude", max_digits=16, decimal_places=8)
    altitude = models.DecimalField("Altitude", max_digits=9, decimal_places=3)
    bearing = models.DecimalField("Bearing", max_digits=9, decimal_places=3)
    accuracy = models.IntegerField("Accuracy")
    speed = models.DecimalField("Speed", max_digits=12, decimal_places=5)
    created_date = models.DateTimeField("Created Date", editable=False, auto_now_add=True)
    updated_date = models.DateTimeField("Updated Date", editable=False, auto_now=True)



class TripAttr(models.Model):
    '''
    MetaData Associated with track
    '''
    trip = models.ForeignKey(Trip, verbose_name="Trip")
    name = models.CharField(max_length=255, blank=False)
    value = models.CharField(max_length=255, blank=False)
    created_date = models.DateTimeField(editable=False, auto_now_add=True)
    updated_date = models.DateTimeField(editable=False, auto_now=True)

