import re
import json
import time
from data.models import Source

def process_youtube(export_comments_response, project_id, source):
    response = export_comments_response
    task_arguments = []
    for elem in response:
            task_argument = {
                'project_id':project_id,
                'text':elem["commentBody"],
                'date':time.strftime('%Y-%m-%d', time.localtime(elem["time"])),
                'source':source,
                'url':"https://www.youtube.com/watch?v={}&lc={}".format(elem['videoId'], elem['commentId']),
            }
            task_arguments.append(task_argument) 
    return task_arguments

source_names = {
    #'twitter':{'source':'Twitter', 'func':process_youtube},
    'youtu':{'source':'YouTube','func':process_youtube},
    #'facebook':{'source':'Facebook','func':process_youtube},
    #'instagram':{'source':'Instagram','func':process_youtube},
    #'tiktok':{'source':'TikTok','func':process_youtube},
}

def get_source(url):
    for key, value in source_names.items():
        if re.search(key, url):
            return Source.objects.get_or_create(label=value["source"])
    return None
    
def get_function(source_name):
    for key, value in source_names.items():
        if re.search(key, source_name.lower()):
            return value["func"]
    return None
