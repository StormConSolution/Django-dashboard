from data.models import Data, Project

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse

LOGIN_URL = '/login/'

@login_required(login_url=LOGIN_URL)
def index(request):
    """
    The home page renders the latest project by default.
    """
    proj = Project.objects.filter(
        users=request.user).latest()
    return redirect(reverse('projects', kwargs={'project_id':proj.id}))


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
    my_projects = Project.objects.filter(users=request.user)
    this_project = get_object_or_404(Project, pk=project_id)
    
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    context = {
        'project_list': my_projects.values(),
        'project':this_project,
    }
    return render(request,  "project.html", context)
