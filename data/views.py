from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q
from django.urls import reverse

from data.models import Data, Project, Aspect, Entity, Charts

import datetime
import json


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


def get_chart_data(this_project, start=datetime.date.today() - datetime.timedelta(days=30), end=datetime.date.today()):

    charts_list = Charts.objects.filter(
        project=this_project).values_list('chart_type', flat=True)

    if 'sentiment_t' in charts_list:
        # TODO Sentiment frequency
        pass
    if 'sentiment_f' in charts_list:
        sentiment_f = Data.objects.filter(project=this_project).aggregate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)), negative=Count('sentiment', filter=Q(sentiment__lt=0)), neutral=Count('sentiment', filter=Q(sentiment=0)))
    if 'aspects_t' in charts_list:
        # TODO:aspects over time
        pass
    if 'aspects_f' in charts_list:
        aspect_f = Aspect.objects.filter(data__project=this_project, data__date_created__range=(
            start, end)).order_by('label').annotate(total_count=Count('label'))

    # Django standart date formater
    """
    print(json.dumps(
        datetime,
        sort_keys=True,
        indent=1,
        cls=DjangoJSONEncoder
    ))
    """
    return {}


@ login_required(login_url=LOGIN_URL)
def projects(request, project_id):

    this_project = get_object_or_404(Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    if request.method == 'POST':

        return JsonResponse(get_chart_data(this_project))

    # Project name for the tab name
    context = {'project_name': this_project}

    # List of projects for the sidebar
    context['project_list'] = list(
        Project.objects.filter(users=request.user).values())

    context['chart_data'] = get_chart_data(this_project)

    return render(request,  "project.html", context)
