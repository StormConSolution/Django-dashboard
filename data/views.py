import collections
from datetime import datetime, timedelta
import json
import time
import requests
from typing import Dict, List

from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Count, Q, F, Sum, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect, QueryDict
from django.http.multipartparser import MultiPartParser
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from data import models as data_models
from data import charts
from data.forms import AlertRuleForm

MAX_TEXT_LENGTH = 30

ASPECT_COLORS = [
    'Pink', 'Crimson', 'Coral', 'Chocolate', 'DarkCyan', 'LightCoral',
    'DarkOliveGreen', 'LightSkyBlue', 'MintCream', 'PowderBlue', 'SandyBrown',
    'Tomato', 'SeaGreen', 'DarkKhaki', 'DarkOrange', 'DarkSlateGray',
    'DeepSkyBlue', 'DimGrey', 'DarkRed', 'Gold', 'IndianRed', 'Lavender',
    'LightGrat', 'LightSlateGray',
]

def collect_args(this_project, request):
    entity_filter = request.GET.get('entity')
    aspect_topic = request.GET.get('aspecttopic')
    aspect_name = request.GET.get('aspectname')

    # getting list of query params
    lang = request.GET.getlist('filter_language')
    src = request.GET.getlist('filter_source')
    # cleaning up the query params
    if lang:
        lang_filter = lang[0].split(",")
    else:
        lang_filter = lang
    if src:
        source_filter = src[0].split(",")
    else:
        source_filter = src

    if this_project.data_set.count() > 0:
        end = this_project.data_set.latest().date_created
    else:
        end = datetime.date.today()
    start = end - datetime.timedelta(days=30)

    if 'from' in request.GET and 'to' in request.GET:
        start = datetime.datetime.strptime(request.GET.get('from'), "%Y-%m-%d")
        end = datetime.datetime.strptime(request.GET.get('to'), "%Y-%m-%d")
    
    return dict(
        project=this_project,
        entity_filter=entity_filter,
        aspect_topic=aspect_topic,
        aspect_name=aspect_name,
        lang_filter=lang_filter,
        source_filter=source_filter,
        start=start,
        end=end,
        request=request
    )

def default_encoder(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def index(request):
    """
    The home page renders the latest project by default.
    """
    proj = data_models.Project.objects.filter(users=request.user)
    if proj:
        proj = proj.latest()
        return redirect(reverse('project'))
    else:
        # return forbiden if no projects, so that there is no crash
        return HttpResponseForbidden()


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
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


class Projects(View):
    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        for project in projects:
            data = data_models.Data.objects.filter(project=project["id"]).aggregate(
            positive_count=Coalesce(Sum(Case(When(sentiment__gt=0, then=1)), output_field=IntegerField()), 0), 
            negative_count=Coalesce(Sum(Case(When(sentiment__lt=0, then=1)), output_field=IntegerField()),0),
            neutral_count=Coalesce(Sum(Case(When(sentiment=0, then=1)), output_field=IntegerField()),0))
            project.update(data)
        context={}
        languages = list(data_models.Data.objects.filter(project__users=user).values("language").distinct().values("language"))
        context["all_languages"] = []
        for element in languages:
            for language_tuple in settings.LANGUAGES:
                if element["language"] == language_tuple[0]:
                    context["all_languages"].append(language_tuple)
        context["all_sources"] = []
        sources = data_models.Data.objects.filter(project__users=user).distinct("source__id").values('source__id', "source__label")
        for element in sources:
            context["all_sources"].append({"label": element["source__label"], "id":element["source__id"]})
        
        context["projects_data"] = projects
        context["projects_count"] = len(projects)
        context["user"] = user
        
        context["all_aspects"] = []
        all_aspects = data_models.AspectModel.objects.filter(users=user).order_by("label")
        for aspect in all_aspects:
            context["all_aspects"].append({"id":aspect.id, "label": aspect.label}) 
        
        context["custom_aspect_models"] = data_models.AspectModel.objects.filter(users=user).values('id', 'label')
        context['standard_aspect_models'] = data_models.AspectModel.objects.filter(standard=True).values('id', 'label')
        
        return render(request, "projects.html", context)
    
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        project_name = request.POST.get("project-name")
        aspect_id = request.POST.get("aspect-id")
        if aspect_id != "-1":
            aspect = data_models.AspectModel.objects.get(pk=aspect_id)
            project = data_models.Project(aspect_model=aspect, name=project_name)
        else:
            project = data_models.Project(name=project_name)
        
        project.save()
        project.users.add(user)
        project.save()
        return redirect("project", project.id)

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def new_project_details(request, project_id):
    user = request.user
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))

    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    context={}
    
    context["projects_data"] = projects
    context["project"] = this_project
    context["user"] = user
    context["sources"] = []
    context["sourceID"] = []
    context["languages"] = []
    
    context["custom_aspect_models"] = data_models.AspectModel.objects.filter(users=user).values('id', 'label')
    context['standard_aspect_models'] = data_models.AspectModel.objects.filter(standard=True).values('id', 'label')
    
    source_query = """select distinct (ds.id) , ds."label", count(ds.id), ds.id from data_source ds inner join data_data dd on ds.id = dd.source_id where dd.project_id = %s group by ds.id order by count(ds.id) desc;"""
    with connection.cursor() as cursor:
        cursor.execute(source_query, [project_id])
        rows = cursor.fetchall()
    for row in rows:
        context["sources"].append({"sourceLabel":row[1], "sourceID":row[3]})
    
    languages = list(data_models.Data.objects.filter(project__users=user).distinct().values("language"))
    context["all_languages"] = []
    for element in languages:
        for language_tuple in settings.LANGUAGES:
            if element["language"] == language_tuple[0]:
                context["all_languages"].append(language_tuple)
        #context["all_languages"].append(element["language"])
    languages = list(data_models.Data.objects.filter(project__users=user, project_id=project_id).distinct().values("language"))
    context["languages"] = []
    for element in languages:
        for language_tuple in settings.LANGUAGES:
            if element["language"] == language_tuple[0]:
                context["languages"].append(language_tuple)
    
    context["all_sources"] = []
    sources = data_models.Data.objects.filter(project__users=user).distinct("source__id").values('source__id', "source__label")
    for element in sources:
        context["all_sources"].append({"label": element["source__label"], "id":element["source__id"]})
    
    if data_models.Data.objects.filter(project=project_id).count() != 0:
        data = data_models.Data.objects.filter(project=project_id).latest('date_created')
        context["default_date_to"] = data.date_created.strftime("%Y-%m-%d")
        #context["default_date_from"] = datetime.strptime(data.date_created, '%Y/%m/%d')
        context["default_date_from"] = (data.date_created - timedelta(days=90)).strftime("%Y-%m-%d")

    return render(request, "project-details.html", context)

def entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)
    table = charts.EntityTable(**args)
    
    return JsonResponse(table.render_data())


def data_entries(request, project_id):
    """
    list all data entries for this project.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)
    table = charts.DataEntryTable(**args)
    
    return JsonResponse(table.render_data())

def aspect_topics(request, project_id):
    """
    Show the frequency of occurence for the topics found in the aspects.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)
    
    table = charts.AspectTopicTable(**args)

    return JsonResponse(table.render_data())


def aspect_name(request, project_id):
    """
    Show the frequency of occurence of the topics related to the given aspect.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)

    table = charts.AspectNameTable(**args)

    return JsonResponse(table.render_data())

def aspect_topic_detail(request, project_id):
    """
    Renders sentiment text for topic specified.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    topic = request.GET.get('topic')

    aspects = data_models.Aspect.objects.filter(
        data__project=this_project,
        topic=topic
    )

    if int(request.GET.get('sentiment')) > 0:
        aspects = aspects.filter(sentiment__gt=0)
    else:
        aspects = aspects.filter(sentiment__lt=0)
    
    data = []
    for a in aspects.values('sentiment_text', 'chunk', 'data__text'):
        for t in a['sentiment_text']:
            if t and t != topic:
                data.append([t, a['data__text']])
    
    return JsonResponse({"data":data})

def aspect_topic_summary(request, project_id):
    """
    Renders sentiment text stats for topic specified.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    topic = request.GET.get('topic')

    aspects = data_models.Aspect.objects.filter(
        data__project=this_project,
        topic=topic
    )

    if int(request.GET.get('sentiment')) > 0:
        aspects = aspects.filter(sentiment__gt=0)
    else:
        aspects = aspects.filter(sentiment__lt=0)
    
    data = collections.defaultdict(int)
    for a in aspects.values('sentiment_text'):
        for t in a['sentiment_text']:
            if t != topic:
                data[t] += 1
    
    return JsonResponse({"data":list(data.items())})

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
    # This user does not have permission to view this project.
        return HttpResponseForbidden()

    aspect_label = request.GET.get('aspect', '')
    sentiment = request.GET.get('sentiment', '')
    with connection.cursor() as cursor:
        if sentiment == 'neutral':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from data_aspect da inner join data_data dd on da.data_id = dd.id where dd.project_id = %s and dd.sentiment = 0 and da."label" = %s""", [this_project.id, aspect_label])
        elif sentiment == 'negative':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from data_aspect da inner join data_data dd on da.data_id = dd.id where dd.project_id = %s and dd.sentiment < 0 and da."label" = %s""", [this_project.id, aspect_label])
        elif sentiment == 'positive':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from data_aspect da inner join data_data dd on da.data_id = dd.id where dd.project_id = %s and dd.sentiment > 0 and da."label" = %s""", [this_project.id, aspect_label])
        rows = cursor.fetchall()
    return JsonResponse(rows, safe=False)

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sentiment_per_entity(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
    # This user does not have permission to view this project.
        return HttpResponseForbidden()
    entities_limit = request.GET.get("max-entities", 8)
    with connection.cursor() as cursor:
        cursor.execute("""
        select dde.entity_id, de."label" , count(dde.entity_id) from data_data_entities dde inner join data_data dd on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id where dd.project_id = %s group by (dde.entity_id, de."label") order by count(dde.entity_id) desc limit %s;
        """, [this_project.id, entities_limit])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        data = data_models.Data.objects.filter(entities__pk = row[0], project_id=project_id)
        negative_count = data.filter(sentiment__lt = 0).count()
        positive_count = data.filter(sentiment__gt = 0).count()
        neutral_count = data.filter(sentiment= 0).count()
        data_response = data.values("sentiment", "text")
        response.append({
            "positive_count": positive_count,
            "neutral_count":neutral_count,
            "negative_count": negative_count,
            "entity_label": row[1],
            "data":list(data_response)
        })

    return JsonResponse(response, safe=False)

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def topics_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
    # This user does not have permission to view this project.
        return HttpResponseForbidden()
    response_data = {'aspects':{}}
    with connection.cursor() as cursor:

        cursor.execute("""
            select da."label" ,da.topic, count(*) from data_aspect da inner join data_data dd on dd.id = da.data_id where dd.project_id = %s group by (da.topic, da."label") order by  da."label" ,count(*) desc;""", [project_id])
        rows = cursor.fetchall()
    for row in rows:
        if row[0] not in response_data['aspects']:
            response_data['aspects'][row[0]] = {}
            response_data['aspects'][row[0]]['topics'] = list()
        else:
            aux = {'topic': row[1], 'count': row[2]}
            response_data['aspects'][row[0]]['topics'].append(aux)
    return JsonResponse(response_data, safe=False)

class AlertRuleList(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        
        context = {}
        context["projects_data"] = data_models.Project.objects.filter(users=user).values("name", "id")

        # Get list of possible aspects. This is slow right now, probably should move to raw SQL.
        all_aspects = data_models.Aspect.objects.filter(
                data__project__users=user).distinct('label')
        for a in all_aspects:
            a.project = a.data.project
        context["all_aspects"] = all_aspects

        context['alerts'] = data_models.AlertRule.objects.filter(project__users=user)

        return render(request, "alertrule-list.html", context)
    
    @method_decorator(login_required)
    def post(self, request):
        form = AlertRuleForm(data=request.POST)
        if form.is_valid():
            form.save()
        return redirect("alerts")

@method_decorator(csrf_exempt, name='dispatch')
class AlertRule(View):
    
    @method_decorator(login_required)
    def delete(self, request, alert_id):
        user = request.user
        rule = data_models.AlertRule.objects.filter(project__users=user, pk=alert_id)
        if rule.count() == 0:
            return HttpResponse(status=403)

        rule.delete()
        return HttpResponse(status=200)

    @method_decorator(login_required)
    def get(self, request, alert_id):
        user = request.user

        rules = data_models.AlertRule.objects.filter(project__users=user, pk=alert_id)
        if rules.count() == 0:
            return HttpResponse(status=403)

        rule = rules.get()
        response = {
            'name':rule.name,
            'project':rule.project_id,
            'aspect':rule.aspect,
            'frequency':rule.frequency,
            'period':rule.period,
            'keywords':rule.keywords,
            'emails':rule.emails,
            'sms':rule.sms,
        }
        
        return JsonResponse(response, safe=False)
    
    @method_decorator(login_required)
    def post(self, request, alert_id):
        user = request.user
        
        rule = data_models.AlertRule.objects.filter(project__users=user, pk=alert_id)
        if rule.count() == 0:
            return HttpResponse(status=403)

        form = AlertRuleForm(instance=rule.get(), data=request.POST)
        if form.is_valid():
            form.save()
        return redirect("alerts")

class AspectsList(View):

    @method_decorator(login_required)
    def get(self, request):
        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page-size", 10))
        user = request.user
        aspect_list = data_models.AspectModel.objects.filter(users=user).order_by("label", "id")
        
        context = {}
        context["aspects"] = []
        context["standard_aspect_models"] = []
        context["custom_aspect_models"] = []
        
        p = Paginator(aspect_list, page_size)
        page = p.page(page_number)
        all_aspects = data_models.AspectModel.objects.filter(users=user).order_by("label")
        
        for aspect in all_aspects:
            context["custom_aspect_models"].append({"id":aspect.id, "label": aspect.label}) 
        
        standard_aspect_models = data_models.AspectModel.objects.filter(standard=True).order_by("label")
        for aspect in standard_aspect_models:
            context["standard_aspect_models"].append({"id":aspect.id, "label": aspect.label}) 

        for aspect in page.object_list:
            rules_list = []
            rules = data_models.AspectRule.objects.filter(aspect_model=aspect)
            for rule in rules:
                rules_list.append(rule.__dict__)
            projects = data_models.Project.objects.filter(users=user, aspect_model=aspect).values("name", "id")
            context["aspects"].append({
                "id":aspect.id,
                "label": aspect.label,
                "lang":aspect.language,
                "rules":rules_list,
                "projects":projects,
            })

        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        context["projects_data"] = projects
        context["page"] = p.get_page(page_number)
        context["paginator"] = p
        context["meta"] = {}
        context["meta"]["page_items_from"] = (page_number - 1) * 10 + 1 
        context["meta"]["page_items_to"] = page_number * 10
        req = requests.get("https://api.repustate.com/v4/%s/classifications.json"%(settings.APIKEY))
        context["classifications"] = json.loads(req.text)
        context["languages"] = settings.LANGUAGES
        languages = list(data_models.Data.objects.filter(project__users=user).values("language").distinct().values("language"))
        context["all_languages"] = []
        for element in languages:
            for language_tuple in settings.LANGUAGES:
                if element["language"] == language_tuple[0]:
                    context["all_languages"].append(language_tuple)
        return render(request, "aspect-list.html", context)
    
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        aspect_label = request.POST.get("aspect-label", "")
        aspect_lang = request.POST.get("aspect-lang", "")
        rule_names = request.POST.getlist("rule-name")
        rule_definitions = request.POST.getlist("rule-definition", "")
        rule_classifications = request.POST.getlist("rule-classification", "")
         
        aspect_model = data_models.AspectModel.objects.create(label=aspect_label, language=aspect_lang, standard=False)
        aspect_model.users.add(user)
        count = 0
        for rule_name in rule_names:
            aspect_definition = data_models.AspectRule(
                rule_name=rule_name,
                definition=rule_definitions[count],
                aspect_model=aspect_model,
                classifications=rule_classifications[count],
            ) 
            aspect_definition.save()
            count += 1
        
        return redirect("aspects")

@method_decorator(csrf_exempt, name='dispatch')
class Aspect(View):
    
    @method_decorator(login_required)
    def delete(self, request, aspect_id):
        user = request.user
        aspect  = data_models.AspectModel.objects.filter(users=user, pk=aspect_id)
        if aspect.count() == 0:
            return HttpResponse(status=403)

       
        aspect.delete()
        return HttpResponse(status=200)

    @method_decorator(login_required)
    def get(self, request, aspect_id):
        user = request.user

        aspect  = data_models.AspectModel.objects.filter(users=user, pk=aspect_id)
        if aspect.count() == 0:
            return HttpResponse(status=403)
        aspect = aspect.get()
        rules = data_models.AspectRule.objects.filter(aspect_model=aspect)
        response = {}
        response["aspect_id"] = aspect.id
        response["aspect_label"] = aspect.label
        response["aspect_lang"] = aspect.language
        response["rules"] = []
        for rule in rules:
            response["rules"].append({
                "rule_label":rule.rule_name,
                "rule_definitions":rule.definition,
                "rule_id":rule.id,
                "rule_classifications": rule.classifications})
        return JsonResponse(response, safe=False)
    
    @method_decorator(login_required)
    def post(self, request, aspect_id):
        method = request.POST.get("_method", "")
        if method == "PUT":
            return self.put(request, aspect_id)
        return HttpResponse("test")

    @method_decorator(login_required)
    def put(self, request, aspect_id):
        user = request.user
        aspect  = data_models.AspectModel.objects.filter(users=user, pk=aspect_id)
        aspect_label = request.POST.get("aspect-label", "")
        aspect_lang = request.POST.get("aspect-lang", "")
        rule_names = request.POST.getlist("rule-name")
        rule_definitions = request.POST.getlist("rule-definition")
        rule_classifications = request.POST.getlist("rule-classification", "")
        rules_id = request.POST.getlist("rule-id", "")

        if aspect.count() == 0:
            return HttpResponse(status=403)

        aspect = aspect.get()
        aspect.label = aspect_label
        aspect.language = aspect_lang
        aspect.save()
        rules = data_models.AspectRule.objects.filter(aspect_model=aspect)

        for rule in rules:
            rule_id = str(rule.id)
            if rule_id not in rules_id:
                rule.delete()

        rules_len = len(rules_id)
        count = 0
        for rule_name in rule_names:
            if count >= rules_len:
                new_rule = data_models.AspectRule.objects.create(
                        rule_name=rule_names[count], 
                        definition=rule_definitions[count], 
                        aspect_model=aspect,
                        classifications=rule_classifications[count])
                continue
            rule_id = rules_id[count]
            rule_to_change = data_models.AspectRule.objects.filter(aspect_model=aspect, pk=rule_id)
            if rule_to_change.count() !=0:
                rule_to_change = rule_to_change.get()
                rule_to_change.definition = rule_definitions[count]
                rule_to_change.label = rule_names[count]
                rule_to_change.classifications = rule_classifications[count]
                rule_to_change.save()
            count = count + 1
        return HttpResponse(status=200)

class SentimentList(View):

    @method_decorator(login_required)
    def get(self, request):
        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page-size", 10))
        user = request.user
        sentiment_list = data_models.Sentiment.objects.filter(users=user)
        context = {}
        context['sentiments'] = []
        p = Paginator(sentiment_list, page_size)
        page = p.page(page_number)
        for sentiment in page.object_list:
            context['sentiments'].append({
                "label":sentiment.label,
                "text": sentiment.definition,
                "language": sentiment.language,
                "sentiment":sentiment.sentiment,
                "rule_id": sentiment.rule_id,
                "id":sentiment.id
            })
        p = Paginator(sentiment_list, page_size)
        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        context["projects_data"] = projects
        context["projects_data"] = projects
        context["page"] = p.get_page(page_number)
        context["paginator"] = p
        context["meta"] = {}
        context["meta"]["page_items_from"] = (page_number - 1) * 10 + 1 
        context["meta"]["page_items_to"] = page_number * 10
        context["languages"] = settings.LANGUAGES
        languages = list(data_models.Data.objects.filter(project__users=user).values("language").distinct().values("language"))
        context["all_languages"] = []
        for element in languages:
            for language_tuple in settings.LANGUAGES:
                if element["language"] == language_tuple[0]:
                    context["all_languages"].append(language_tuple)
        return render(request, "sentiment-list.html", context)
    
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        sentiment_label = request.POST.get("sentiment-label", "")
        text_definition = request.POST.get("sentiment-definition", "")
        sentiment = request.POST.get("sentiment", "")
        sentiment_language = request.POST.get("sentiment-language", "")
        if sentiment_label == "":
            return HttpResponse("Sentiment Name is empty", status = 400)
        text_definition_count = len(text_definition.split())
        if text_definition_count < 1 or text_definition_count > 3:
            return HttpResponse("Text Definition need to have at least 1 word and a maximum of 3 words", status = 400)
        if sentiment == "positive":
            sentiment_value = "pos"
        elif sentiment == "negative":
            sentiment_value = "neg"
        elif sentiment == "neutral":
            sentiment_value = "neu"
        data = {
            "text":text_definition,
            "sentiment":sentiment_value,
            "lang": sentiment_language
        }
        #aspect_definition = data_models.AspectDefinition(aspect_model=aspect_model)
        req = requests.post('%s/v4/%s/sentiment-rules.json' % (settings.API_HOST, settings.APIKEY), data=data)
        json_data = json.loads(req.text)
        sentiment_model = data_models.Sentiment(
            label=sentiment_label,
            definition=text_definition,
            sentiment=sentiment,
            language=sentiment_language,
            rule_id = json_data["rule_id"]
        )
        sentiment_model.save() 
        sentiment_model.users.add(user)

        return redirect("sentiment")

@method_decorator(csrf_exempt, name='dispatch')
class Sentiment(View):
    @method_decorator(login_required)
    def delete(self, request, sentiment_id):
        user = request.user

        sentiment = get_object_or_404(data_models.Sentiment, pk=sentiment_id, users=user)
       
        requests.delete("%s/v4/%s/sentiment-rules.json?rule_id=%s" % (settings.API_HOST, settings.APIKEY, sentiment.rule_id))
        sentiment.delete()
        return HttpResponse(status=200)

    @method_decorator(login_required)
    def post(self, request, sentiment_id):
        user = request.user
        sentiment_label = request.POST.get("sentiment-label", "")
        text_definition = request.POST.get("sentiment-definition", "")
        sentiment_value = request.POST.get("sentiment", "")
        sentiment_language = request.POST.get("sentiment-language", "")
        sentiment = get_object_or_404(data_models.Sentiment, pk=sentiment_id, users=user)
        if sentiment_label == "":
            return HttpResponse("Sentiment Name is empty", status = 400)
        text_definition_count = len(text_definition.split())
        if text_definition_count < 1 or text_definition_count > 3:
            return HttpResponse("Text Definition need to have at least 1 word and a maximum of 3 words", status = 400)
        requests.delete("%s/v4/%s/sentiment-rules.json?rule_id=%s" % (settings.API_HOST, settings.APIKEY, sentiment.rule_id))
        data = {
            "text":text_definition,
            "sentiment":sentiment_value,
            "lang": sentiment_language
        }
        req = requests.post('%s/v4/%s/sentiment-rules.json' % (settings.API_HOST, settings.APIKEY), data=data)
        json_data = json.loads(req.text)
        sentiment.label = sentiment_label
        sentiment.definition = text_definition
        sentiment.sentiment = sentiment_value
        sentiment.language = sentiment_language
        sentiment.rule_id = json_data["rule_id"]

        sentiment.save()
        return HttpResponse(status=200)
