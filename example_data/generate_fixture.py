import django
import os
import db_scripts

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

# Model imports have to be after 
from data.models import *


Project.objects.all().delete()
Data.objects.all().delete()

db_scripts.create_new_project("Project 1")
user_id = db_scripts.create_user("test2","123@gmail.com",'123')
db_scripts.assign_user_to_project(Project.objects.get(name = 'Project 1').id,user_id)

aspects = open('example_data/AR.txt').readlines()
text = open('example_data/raw.txt')

this_project = Project.objects.get(name = 'Project 1')

for i,line in enumerate(text):
    db_scripts.add_data(this_project,'twitter',line,'en',True,aspect_model=None,aspect=aspects[i])
