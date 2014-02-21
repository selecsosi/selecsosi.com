import csv
from datetime import datetime
from .models import GpsPoint, Trip
from django.contrib.auth.models import User
from django.core.files import File


class CsvFileUploadHelper:

    def parse_trip_data_into_geopoints(self, trip):
        path = trip.route_csv.path
        with open(path, 'rb') as csv_file:
            records = csv.reader(csv_file)
            ln_cnt = 0
            for row in records:
                if ln_cnt < 4:
                    if ln_cnt == 1:
                        trip.date = datetime.strptime(row[0], "%m/%d/%Y %H:%M")
                        trip.save()
                else:
                    d = datetime.strptime(row[8], "%Y-%m-%dT%H:%M:%S.000Z")
                    g_point = GpsPoint(trip=trip, date=d, segment=row[0],
                        point=row[1], lat=row[2], lng=row[3],
                        altitude=row[4], bearing=row[5], accuracy=row[6],
                        speed=row[7])
                    g_point.save()
                ln_cnt += 1

    def parse_csvs_into_trip_and_geopoints(self, paths):
        user = User.objects.get(username='selecsosi')
        trip_list = []
        for path in paths:
            f = open(path, 'rb')
            print "Working with file %s" % f.name
            route_csv = File(f)
            #csv_reader = csv.reader(f)
            # get Title row, 9/9/2012  1:34:00 AM
            #csv_reader.next()
            #row = csv_reader.next()
            #date = datetime.strptime(row[0], "%d/%m/%Y %H:%M:%S %p")
            name = f.name.split('/')[-1] + " Drive"
            t = Trip(user=user, route_csv=route_csv, name=name)
            t.save()
            trip_list.append(t)
            f.close()

        for trip in trip_list:
            self.parse_trip_data_into_geopoints(trip)
