import os
import django
import csv
import sys

from django.core.wsgi       import get_wsgi_application
application = get_wsgi_application()

from users.models import Region,SubRegion

os.environ.setdefault("DJANGO_SETTINGS_MODULE","bestgo.settings")
django.setup()


CSV_PATH_REGIONS = './subregions.csv'

with open(CSV_PATH_REGIONS) as in_file:
    data_reader = csv.reader(in_file)
    next(data_reader,None)
    for row in data_reader:
        region_name = row[0]
        if not Region.objects.filter(name=region_name).exists():
            Region.objects.create(name =region_name)
        which_region = Region.objects.get(name=row[0])
        SubRegion.objects.create(region=which_region, name=row[1])