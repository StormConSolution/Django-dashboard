from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from data.models import Data, Project
from django import template


@login_required(login_url="/login/")
def index(request):
    a = Project.objects.filter(
        users=request.user).values_list('id').order_by('id')[0][0]

    return redirect('/projects/'+str(a)+'/')


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
    a = Project.objects.filter(users=request.user)
    print(a)
    context = {'project_list': list(a.values())}

    return render(request,  "project.html", context)
