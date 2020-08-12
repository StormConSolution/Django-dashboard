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

from data.models import Data, Project, Aspect, Entity, Chart, EmotionalEntity, Emotion

LOGIN_URL = '/login/'

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

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


def get_chart_data(this_project, start, end, entity_filter):

    charts_list = Chart.objects.filter(
        project=this_project).values_list('chart_type', flat=True)
    
    result = {"status": "OK", "data": [], 'list': list(charts_list)}
    aspect_data_set = Aspect.objects.filter(
        data__project=this_project,
        data__date_created__range=(start, end)
    )

    data_set = Data.objects.filter(
        project=this_project,
        date_created__range=(start, end)
    )

    if entity_filter:
        aspect_data_set = aspect_data_set.filter(
            data__entities__label=entity_filter)
        data_set = data_set.filter(entities__label=entity_filter)

    if 'sentiment_t' in charts_list:
        sentiment_t = data_set.values('date_created').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        ).order_by('date_created')

        result['data'].append({"sentiment_t":list(sentiment_t)})

    if 'sentiment_f' in charts_list:
        sentiment_f = data_set.aggregate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        )
        result['data'].append({"sentiment_f": [sentiment_f]})

    if 'aspect_t' in charts_list:
        aspect_t = aspect_data_set.values('label').annotate(Count('label')).annotate(data__date_created=F("data__date_created")).order_by("data__date_created")
        result['data'].append({"aspect_t":list(aspect_t)})

    if 'aspect_f' in charts_list:
        aspect_f = aspect_data_set.values('label').annotate(
            Count('label')).order_by('label')

        result['data'].append({"aspect_f": list(aspect_f)})

    if 'aspect_s' in charts_list:
        aspect_s = aspect_data_set.values('label').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        )
        
        result['data'].append({"aspect_s": list(aspect_s)})
    
    # Get the chart data for the heatmap. For now, load it regardless of any
    # flags being present in charts_list.
    if True:
        # Grab the top 10 entities mentioned with emotion.
        top_ten_entities = EmotionalEntity.objects.annotate(
                entity_count=models.Count('entity')).order_by('-entity_count')[:10]

        result['entities_for_emotions'] = json.dumps([
            e.entity.label for e in top_ten_entities
        ])
        
        top_ten_emotions = EmotionalEntity.objects.annotate(
                emotion_count=models.Count('emotion')).order_by('-emotion_count')[:10]
        
        emotion_count = {}
        for e in Emotion.objects.all():
            emotion_count[e.label] = EmotionalEntity.objects.filter(emotion=e).count()

        sorted_emotion = sorted(emotion_count.items(), key=lambda item:item[1])
        result['emotions'] = json.dumps([
            k for k,v  in sorted_emotion
        ])
    
    return json.dumps(result, sort_keys=True, default=default)


@login_required(login_url=LOGIN_URL)
def projects(request, project_id):

    this_project = get_object_or_404(Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    entity_filter = request.GET.get('entity')

    default_start = datetime.date.today() - datetime.timedelta(days=30)
    default_end = datetime.date.today()

    start = request.GET.get('start', default_start)
    end = request.GET.get('end', default_end)

    context = {
        'project': this_project,
        'chart': get_chart_data(this_project, start, end, entity_filter),
        'query_string': request.GET.urlencode(),
    }

    # List of projects for the sidebar
    context['project_list'] = list(
        Project.objects.filter(users=request.user).values())
  
    return render(request,  "project.html", context)


def entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    entity_set = Entity.objects.all()
    if 'entity' in request.GET:
        entity_set = entity_set.filter(
            data__in=Data.objects.filter(entities__label=request.GET['entity']))

    entity_count = entity_set.annotate(
        data_count=models.Count('data')).order_by('-data_count')
    entities = {"data": []}

    for ec in entity_count:
        entities["data"].append([
            ec.label,
            ', '.join(ec.classifications.values_list('label', flat=True)),
            ec.data_count
        ])

    return JsonResponse(entities)
