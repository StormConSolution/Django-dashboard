import datetime
import json

from django import template
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Count, Q, F
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse

from data import models as data_models
from data import charts

LOGIN_URL = '/login/'



def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


@login_required(login_url=LOGIN_URL)
def index(request):
    """
    The home page renders the latest project by default.
    """
    proj = data_models.Project.objects.filter(users=request.user)
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


def get_chart_data(this_project, start, end, entity_filter):
    charts_list = this_project.charts.values_list('chart_type', flat=True)

    result = {"status": "OK", 'list': list(charts_list)}
    for chart_type in charts_list:
        instance = charts.CHART_LOOKUP[chart_type](this_project, start, end, entity_filter)
        data = instance.render_data()
        for key,value in data.items():
            result[key] = value

    return json.dumps(result, sort_keys=True, default=default)


@login_required(login_url=LOGIN_URL)
def projects(request, project_id):

    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    entity_filter = request.GET.get('entity')

    default_start = str(datetime.date.today() - datetime.timedelta(days=30))
    default_end = str(datetime.date.today())

    start = datetime.datetime.strptime(request.GET.get('start', default_start),"%Y-%m-%d")
    end = datetime.datetime.strptime(request.GET.get('end', default_end),"%Y-%m-%d")    
         

    context = {
        'project': this_project,
        'chart_data': get_chart_data(this_project, start, end, entity_filter),
        'query_string': request.GET.urlencode(),
        'start_date': start,
        'end_date': end
    }

    # List of projects for the sidebar
    context['project_list'] = list(
        data_models.Project.objects.filter(users=request.user).values())

    return render(request,  "project.html", context)


def entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    default_start = datetime.date.today() - datetime.timedelta(days=30)
    default_end = datetime.date.today()

    # TODO: pass the start/end values.
    start = request.GET.get('start', default_start)
    end = request.GET.get('end', default_end)

    table = charts.EntityTable(
        this_project, start, end, request.GET.get('entity'))
    return JsonResponse(table.render_data())
