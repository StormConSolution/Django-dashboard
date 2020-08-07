from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from data.models import Data, Project
from django import template
from django.core.serializers.json import DjangoJSONEncoder

import datetime
import json


def date_handler(obj): return (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)


@ login_required(login_url="/login/")
def index(request):

    all_projects = Project.objects.filter(users=request.user)
    if all_projects:
        default_project_id = all_projects.values_list(
            'id').order_by('id')[0][0]
    else:
        default_project_id = -1
    return redirect('/projects/'+str(default_project_id)+'/')


@ login_required(login_url="/login/")
def pages(request):

    context = {}

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))


def projects(request, num=-1):
    data_points = []

    list_of_projects = list(
        Project.objects.filter(users=request.user).values())

    for project in list_of_projects:
        if project['id'] == num:
            data_points = list(Data.objects.filter(project=num).values())
    # Django standart date formater
    """ 
    print(json.dumps(
        data_points[0]['date_created'],
        sort_keys=True,
        indent=1,
        cls=DjangoJSONEncoder
    ))
    """

    for i in data_points:
        i['date_created'] = json.dumps(i['date_created'], default=date_handler)
    context = {}
    data = json.dumps({"data": data_points})
    if data_points:
        context['project_data'] = data
    if list_of_projects:
        context['project_list'] = list_of_projects

    return render(request,  "project.html", context)
