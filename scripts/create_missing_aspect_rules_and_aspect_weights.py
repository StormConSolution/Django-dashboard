import sys
import os
from pathlib import Path
sys.path.append(os.path.join(Path(__file__).parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")
from django import setup
from django.db import connection
setup()
from data import models

def run():
    with connection.cursor() as cursor:
        cursor.execute("select id, aspect_model_id from data_project")
        projects_id = cursor.fetchall()
        for aux in projects_id:
            project_id = aux[0]
            aspect_model_id = aux[1]
            print(aspect_model_id)
            if aspect_model_id:
                with connection.cursor() as data_cursor: 
                    data_cursor.execute('select distinct(da."label") from data_aspect da inner join data_data dd on dd.id=da.data_id where dd.project_id = %s', [project_id])
                    labels = data_cursor.fetchall()
                    for label in labels:
                        aspect_model = models.AspectModel.objects.get(id=aspect_model_id)
                        project = models.Project.objects.get(id=project_id)
                        [aspect_rule, created] = models.AspectRule.objects.get_or_create(rule_name=label[0], aspect_model=aspect_model)
                        models.AspectWeight.objects.get_or_create(aspect_rule=aspect_rule, project=project)
           
if __name__ == "__main__":
    run()       
