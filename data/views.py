from data.models import Data, Project

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from data.models import Data, Project
from django import template
from django.core.serializers.json import DjangoJSONEncoder

import datetime
import json

from django.urls import reverse

LOGIN_URL = '/login/'


def date_handler(obj): 
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return None

@login_required(login_url=LOGIN_URL)
def index(request):
    """
    The home page renders the latest project by default.
    """
    proj = Project.objects.filter(users=request.user)
    if proj:
        proj = proj.latest()
        return redirect(reverse('projects', kwargs={'project_id': proj.id}))
    else:
        # return forbiden if no projects, so that there is no crash
        return HttpResponseForbidden()


@login_required(login_url=LOGIN_URL)
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


@login_required(login_url=LOGIN_URL)
def projects(request, project_id):
    list_of_projects = list(
        Project.objects.filter(users=request.user).values())
    this_project = get_object_or_404(Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()
    
    # TODO: aspect query
    # Aspect.objects.filter(data__project=this_project,
    # data__date_created__range=(start,
    # end)).order_by('label').annotate(total_count=Sum('count'))

    data_points = list(Data.objects.filter(project=project_id).values())

    # Django standart date formater
    """ 
    print(json.dumps(
        data_points[0]['date_created'],
        sort_keys=True,
        indent=1,
        cls=DjangoJSONEncoder
    ))
    """
    # Change date to ISO 8601 for js
    for i in data_points:
        i['date_created'] = json.dumps(i['date_created'], default=date_handler)

    context = {}
    data = json.dumps({"data": data_points})
    if data_points:
        context['project_data'] = data
    if list_of_projects:
        context['project_list'] = list_of_projects

    return render(request,  "project.html", context)
