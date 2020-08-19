import django
import os
import db_scripts
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

# Model imports have to be after 
from data.models import *
id = sys.argv[1]

db_scripts.add_chart_to_project(id,"sentiment_f")
db_scripts.add_chart_to_project(id,"sentiment_t")
db_scripts.add_chart_to_project(id,"aspect_f")
db_scripts.add_chart_to_project(id,"aspect_t")
db_scripts.add_chart_to_project(id,"aspect_s")
db_scripts.add_chart_to_project(id,"sentiment_source")
db_scripts.add_chart_to_project(id,'emotional_entities')


