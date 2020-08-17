import django
import os
import db_scripts
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

# Model imports have to be after 
from data.models import *
id = sys.argv[1]

db_scripts.add_chart_to_project(id,"sentiment_f",1)
db_scripts.add_chart_to_project(id,"sentiment_t",2)
db_scripts.add_chart_to_project(id,"aspect_f",1)
db_scripts.add_chart_to_project(id,"aspect_t",2)
db_scripts.add_chart_to_project(id,"aspect_s",2)
db_scripts.add_chart_to_project(id,"sentiment_source",2)
db_scripts.add_chart_to_project(id,'emotional_entities',2)


