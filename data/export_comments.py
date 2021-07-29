import re
import json
import time
from data.models import Source


def process_youtube(export_comments_response, project_id, source):
    response = export_comments_response
    task_arguments = []
    for elem in response:
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
    response = export_comments_response
    task_arguments = []
    for k, elem in response.items():
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
    response = export_comments_response
    task_arguments = []
    for elem in response:
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
    response = export_comments_response
    task_arguments = []
    for elem in response:
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
    response = export_comments_response
    task_arguments = []
    for elem in response:
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
    response = export_comments_response
    task_arguments = []
    for k, elem in response.items():
        task_argument = {
            "project_id": project_id,
            "text": elem["message"],
            "date": time.strftime("%Y-%m-%d", time.localtime(int(elem["time"]))),
            "source": source,
            "url": elem["videoPreviewUrl"],
        }
        task_arguments.append(task_argument)
    return task_arguments


source_names = {
    "twitter": {"source": "Twitter", "func": process_twitter},
    "youtu": {"source": "YouTube", "func": process_youtube},
    'facebook':{'source':'Facebook','func':process_facebook},
    "instagram": {"source": "Instagram", "func": process_instagram},
    'tiktok':{'source':'TikTok','func':process_tiktok},
    'twitch':{'source':'Twitch','func':process_twitch},
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
