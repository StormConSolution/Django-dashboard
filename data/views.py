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

    charts_list = data_models.Chart.objects.filter(
        project=this_project).values_list('chart_type', flat=True)
    
    result = {"status": "OK", "data": [], 'list': list(charts_list)}
    aspect_data_set = data_models.Aspect.objects.filter(
        data__project=this_project,
        data__date_created__range=(start, end)
    )

    data_set = data_models.Data.objects.filter(
        project=this_project,
        date_created__range=(start, end)
    )

    if entity_filter:
        aspect_data_set = aspect_data_set.filter(
            data__entities__label=entity_filter)
        data_set = data_set.filter(entities__label=entity_filter)

    if True or 'sentiment_t' in charts_list:
        sentiment_t = data_set.values('date_created').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        ).order_by('date_created')

        result['data'].append({"sentiment_t":list(sentiment_t)})

    if True or 'sentiment_f' in charts_list:
        sentiment_f = data_set.aggregate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        )
        result['data'].append({"sentiment_f": [sentiment_f]})

    if True or 'aspect_t' in charts_list:
        aspect_t = aspect_data_set.values('label').annotate(Count('label')
                ).annotate(data__date_created=F("data__date_created")
                ).order_by("data__date_created")
        result['data'].append({"aspect_t":list(aspect_t)})

    if True or 'aspect_f' in charts_list:
        aspect_f = aspect_data_set.values('label').annotate(
            Count('label')).order_by('label')

        result['data'].append({"aspect_f": list(aspect_f)})

    if True or 'aspect_s' in charts_list:
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
        top_ten_entities = data_models.Entity.objects.filter(data__in=data_set).annotate(
                data_count=Count('data')).order_by('-data_count')
        result['entities_for_emotions'] = [e.label for e in top_ten_entities]
        
        top_ten_emotions = data_models.EmotionalEntity.objects.filter(entity__in=top_ten_entities).annotate(
                emotion_count=models.Count('emotion')).order_by('-emotion_count')[:10]
        
        emotion_count = {}
        for e in data_models.Emotion.objects.all():
            emotion_count[e.label] = data_models.EmotionalEntity.objects.filter(emotion=e).count()
        
        sorted_emotion = sorted(emotion_count.items(), key=lambda item:item[1])
        result['emotions'] = [k for k,v  in sorted_emotion]
    
    if True:
        # Show sentiment by source.
        result['source_datasets'] = []
        result['source_labels'] = list(data_models.Source.objects.values_list('label', flat=True))
        
        positive = {'label':'positive', 'data':[], 'backgroundColor':'rgba(255, 99, 132, 0.2)'}
        negative = {'label':'negative', 'data':[], 'backgroundColor':'rgba(54, 162, 235, 0.2)'}

        for label in result['source_labels']:
            positive['data'].append(data_models.Data.objects.filter(
                date_created__range=(start, end), source__label=label, sentiment__gt=0).count())
            
            negative['data'].append(data_models.Data.objects.filter(
                date_created__range=(start, end), source__label=label, sentiment__lt=0).count())
            
        result['source_datasets'] = [positive, negative]

    return json.dumps(result, sort_keys=True, default=default)

@login_required(login_url=LOGIN_URL)
def projects(request, project_id):

    this_project = get_object_or_404(data_models.Project, pk=project_id)
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
        'chart_data': get_chart_data(this_project, start, end, entity_filter),
        'query_string': request.GET.urlencode(),
        'start_date':start,
        'end_date':end
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

    table = charts.EntityTable(this_project, start, end, request.GET.get('entity'))
    return JsonResponse(table.render_data())
