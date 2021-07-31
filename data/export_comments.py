import json
import re
import time

from data.models import Source

"""
Each function below is responsible for handling data ingested from that
particular source. While similar, they do all differ slightly in the name of
arguments they receive.
"""

def process_youtube(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response:
        task_argument = {
            "project_id": project_id,
            "text": elem["commentBody"],
            "date": time.strftime("%Y-%m-%d", time.localtime(elem["time"])),
            "source": source,
            "url": "https://www.youtube.com/watch?v={}&lc={}".format(
                elem["videoId"], elem["commentId"]
            ),
        }
        task_arguments.append(task_argument)
    return task_arguments


def process_twitter(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response.values():
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": time.strftime("%Y-%m-%d", time.localtime(elem["time"])),
            "source": source,
            "url": elem["statusUrl"],
        }
        task_arguments.append(task_argument)
    return task_arguments


def process_instagram(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response:
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": time.strftime("%Y-%m-%d", time.localtime(int(elem["time"]))),
            "source": source,
            "url": elem["url"],
        }
        task_arguments.append(task_argument)
    return task_arguments


def process_tiktok(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response:
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": time.strftime("%Y-%m-%d", time.localtime(int(elem["time"]))),
            "source": source,
            "url": elem["commentUrl"],
        }
        task_arguments.append(task_argument)
    return task_arguments

def process_facebook(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response:
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": time.strftime("%Y-%m-%d", time.localtime(int(elem["time"]))),
            "source": source,
            "url": "https://www.facebook.com/{}?comment_id={}".format(elem["postId"], elem["commentId"]),
        }
        task_arguments.append(task_argument)
    return task_argument


def process_twitch(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response.values():
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": time.strftime("%Y-%m-%d", time.localtime(int(elem["time"]))),
            "source": source,
            "url": elem["videoPreviewUrl"],
        }
        task_arguments.append(task_argument)
    return task_arguments


def process_vimeo(export_comments_response, project_id, source):
    
    task_arguments = []
    for elem in export_comments_response:
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": elem["time"].split(" ")[0],
            "source": source,
        }
        task_arguments.append(task_argument)
    return task_arguments


source_names = {
    "twitter": {"source": "Twitter Comments", "func": process_twitter},
    "youtu": {"source": "YouTube Comments", "func": process_youtube},
    'facebook':{'source':'Facebook Comments','func':process_facebook},
    'instagram': {"source": "Instagram Comments", "func": process_instagram},
    'tiktok':{'source':'TikTok Comments','func':process_tiktok},
    'twitch':{'source':'Twitch Comments','func':process_twitch},
    'vimeo':{'source':'Vimeo Comments','func':process_vimeo},
}


def get_source(url):
    """
    Map a URL to an existing Source object.
    """
    for key, value in source_names.items():
        if re.search(key, url):
            return Source.objects.get_or_create(label=value["source"])
    return None


def get_function(source_name):
    """
    Dispatcher that maps a source name to a source function.
    """
    for key, value in source_names.items():
        if re.search(key, source_name.lower()):
            return value["func"]
    return None
