import sys
import os
from pathlib import Path
sys.path.append(os.path.join(Path(__file__).parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")
from django import setup
from django.db import connection
setup()

count = 0
with connection.cursor() as cursor:
    cursor.execute("select * from data_data dd")
    rows = cursor.fetchall()
    for row in rows:
        count = count + 1
        print(count)
        data_id = row[0]
        data_text = row[3]
        with connection.cursor() as aspect_cursor:
            aspect_cursor.execute("select * from data_aspect da inner join data_data dd on dd.id = da.data_id where dd.id = %s", [data_id]) 
            aspect_rows = aspect_cursor.fetchall()
            aspects = ""
            for aspect_row in aspect_rows:
                aspects = "{} {}".format(aspects, aspect_row[1])
        with connection.cursor() as entity_cursor:
            entity_cursor.execute("select * from data_entity de inner join data_data_entities dde on dde.entity_id = de.id inner join data_data dd on dd.id = dde.data_id where dd.id = %s",[data_id])
            entity_rows = entity_cursor.fetchall()
            entities = ""
            for entity_row in entity_rows:
                entities = "{} {}".format(entities, entity_row[1])
        search_text = "{} {} {}".format(data_text, aspects, entities)
        with connection.cursor() as update_cursor:
            update_cursor.execute("update data_data dd set \"search\" = to_tsvector(%s) where dd.id=%s", [search_text, data_id])
    #print(rows)