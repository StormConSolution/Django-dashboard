from data.models import Data, Project

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse


@login_required(login_url="/login/")
def index(request):
    """
    The home page renders the latest project by default.
    """
    proj = Project.objects.filter(
        users=request.user).latest()
    return redirect(reverse('projects', kwargs={'project_id':proj.id}))


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

def projects(request, project_id):
    my_projects = Project.objects.filter(users=request.user)
    context = {
        'project_list': my_projects.values(),
    }
    return render(request,  "project.html", context)
