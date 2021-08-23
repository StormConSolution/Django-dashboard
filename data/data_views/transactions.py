from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from data import models


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def transactions(request):
    user = request.user
    projects = list(models.Project.objects.filter(users=user).values("name", "id"))
    page_number = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page-size", 10))
    export_comments_list = models.ExportComments.objects.filter(project__users=user).prefetch_related('source').order_by('-id')
    context = {}
    p = Paginator(export_comments_list, page_size)
    page = p.get_page(page_number)
    context['export_comments_list'] = page.object_list
    context["projects_data"] = projects
    context["languages"] = settings.LANGUAGES
    context["paginator"] = p
    context["page"] = page
    context["meta"] = {}
    context["meta"]["total"] = len(export_comments_list)
    context["meta"]["page_items_from"] = (page_number - 1) * 10 + 1
    context["meta"]["page_items_to"] = page_number * 10

    return render(request, "transactions.html", context)
