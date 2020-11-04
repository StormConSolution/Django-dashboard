import datetime
import json
from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests
from data import models as data_models
from data import charts

LOGIN_URL = '/login/'


def default_encoder(o):
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


def get_chart_data(this_project, start, end, entity_filter, aspect_topic, aspect_name):
    result = {
        "status": "OK",
        "colors": charts.COLORS["contrasts"],
    }

    for chart in this_project.charts.all():
        if chart.load_async:
            continue
        instance = charts.CHART_LOOKUP[chart.label](
            this_project, start, end, entity_filter, aspect_topic, aspect_name)
        data = instance.render_data()
        for key, value in data.items():
            result[key] = value

    return json.dumps(result, sort_keys=True, default=default_encoder)


@login_required(login_url=LOGIN_URL)
def projects(request, project_id):
    # TODO-  aspects_total_data - test data, write function to compute element
    # TODO - date filter
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseRedirect(LOGIN_URL)

    entity_filter = request.GET.get('entity')
    aspect_topic = request.GET.get('aspecttopic')
    aspect_name = request.GET.get('aspectname')

    # Find the most recent data item.
    if this_project.data_set.count() > 0:
        end = this_project.data_set.order_by('-date_created')[0].date_created
    else:
        end = datetime.date.today()
    start = end - datetime.timedelta(days=30)

    if 'start' in request.GET and 'end' in request.GET:
        start = datetime.datetime.strptime(
            request.GET.get('start'), "%Y-%m-%d")
        end = datetime.datetime.strptime(request.GET.get('end'), "%Y-%m-%d")

    context = {
        'project': this_project,
        'chart_data': get_chart_data(this_project, start, end, entity_filter, aspect_topic, aspect_name),
        'query_string': request.GET.urlencode(),
        'start_date': start,
        'end_date': end,
    }

    # List of projects for the sidebar
    context['project_list'] = list(
        data_models.Project.objects.filter(users=request.user).values())
    context['aspects_total_data'] = []
    chart_data = json.loads(context['chart_data'])
    total_sum = 0
    color_index = 0
    colors = ['pink', 'red', 'purple', 'deep-purple', 'indigo', 'blue', 'light-blue', 'cyan', 'teal', 'green',
              'light-green', 'lime', 'yellow', 'amber']
    for aspect in chart_data['aspect_t_labels']:
        aspect_data = dict()
        aspect_data['name'] = aspect
        aspect_data['total_data'] = sum(
            item['label__count'] for item in chart_data['aspects'][aspect])
        aspect_data['color'] = colors[color_index]
        if color_index == len(colors) - 1:
            color_index = 0
        total_sum += aspect_data['total_data']
        color_index += 1
        context['aspects_total_data'].append(aspect_data)
    for i in range(len(chart_data['aspect_t_labels'])):
        positive_data = chart_data['aspect_s_data'][0]['data'][i]
        negative_data = chart_data['aspect_s_data'][1]['data'][i]
        context['aspects_total_data'][i]['net_data'] = positive_data - negative_data

    for i in range(len(context['aspects_total_data'])):
        context['aspects_total_data'][i]['width'] = (
            context['aspects_total_data'][i][
                'total_data'] / total_sum) * 100
    context['total_data'] = sum(chart_data['sentiment_f_data'])
    context['total_positive'] = chart_data['sentiment_f_data'][0]
    context['total_negative'] = chart_data['sentiment_f_data'][1]
    print(context)
    return render(request, "project_new.html", context)


def top_entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    default_start = datetime.date.today() - datetime.timedelta(days=30)
    default_end = datetime.date.today()

    start = request.GET.get('start', default_start)
    end = request.GET.get('end', default_end)

    table = charts.TopEntityTable(
        this_project, start, end, request.GET.get(
            'entity'), request.GET.get('aspecttopic'),
        request.GET.get('aspectname'),
    )

    return JsonResponse(table.render_data())


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

    start = request.GET.get('start', default_start)
    end = request.GET.get('end', default_end)

    table = charts.EntityTable(
        this_project, start, end, request.GET.get(
            'entity'), request.GET.get('aspecttopic'), request.GET.get('aspectname')
    )
    return JsonResponse(table.render_data())


def aspect_topics(request, project_id):
    """
    Show the frequency of occurence for the topics found in the aspects.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    default_start = datetime.date.today() - datetime.timedelta(days=30)
    default_end = datetime.date.today()

    start = request.GET.get('start', default_start)
    end = request.GET.get('end', default_end)
    table = charts.AspectTopicTable(
        this_project, start, end, request.GET.get(
            'entity'), request.GET.get('aspecttopic'), request.GET.get('aspectname'),
    )


    return JsonResponse(table.render_data())


def aspect_name(request, project_id):
    """
    Show the frequency of occurence of the topics related to the given aspect.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    default_start = datetime.date.today() - datetime.timedelta(days=30)
    default_end = datetime.date.today()

    start = request.GET.get('start', default_start)
    end = request.GET.get('end', default_end)

    table = charts.AspectNameTable(
        this_project, start, end, request.GET.get(
            'entity'), request.GET.get('aspecttopic'), request.GET.get('aspectname'),
    )

    return JsonResponse(table.render_data())


@csrf_exempt
def create_project(request):
    """
    API endpoint for creating a project. May need some work as we go.

    `project_name`: the name of the Project. If it doesn't exist, create it.
    `username`: the user name to add to this project. User is assumed to exist.
    """
    if 'name' not in request.POST or 'username' not in request.POST:
        return JsonResponse({"status": "Fail", "description": "Both `name` and `username` are required"})

    proj, _ = data_models.Project.objects.get_or_create(
        name=request.POST['name'])
    user, _ = User.objects.get_or_create(username=request.POST['username'])
    proj.users.add(user)

    return JsonResponse({"status": "OK", "project_id": proj.id})


@csrf_exempt
def add_data(request, project_id):
    """
    Temporary API endpoint for loading data. May need some work as we go.
    Required: 
    source: where did the text come from, create if doesn't exist
    text: the text itself
    lang: language of the text
    with_entities=0/1: should we extract entities
    aspect_model: which aspect model, if any, to use
    date: date this item was created, defaults today
    """

    text = request.POST['text']
    lang = request.POST.get('lang', 'en')

    try:
        sentiment = requests.post('{HOST}/v4/{APIKEY}/score.json'.format(
            HOST=settings.HOST, APIKEY=settings.APIKEY), {'text': text, 'lang': lang}).json()['score']
    except:
        return JsonResponse({"status": "FAIL", "message": "Could not add text = {} lang = {}".format(text, lang)})

    source, _ = data_models.Source.objects.get_or_create(
        label=request.POST['source'])

    data = data_models.Data.objects.create(
        date_created=request.POST.get('date', datetime.datetime.now().date()),
        project=data_models.Project.objects.get(pk=project_id),
        source=source,
        text=text,
        sentiment=sentiment,
        language=lang,
    )
    emotions = []
    found_entities = []

    entities = {}
    if request.POST.get('with_entities'):
        entities = requests.post('{HOST}/v4/{APIKEY}/entities.json'.format(
            HOST=settings.HOST, APIKEY=settings.APIKEY), {'text': text, 'lang': lang}).json()

    for ent in entities.get('entities', []):
        entity_instance, created = data_models.Entity.objects.get_or_create(
            label=ent['title']
        )

        is_emotion = False

        for clas in ent['classifications']:
            c_instance, created = data_models.Classification.objects.get_or_create(
                label=clas
            )
            entity_instance.classifications.add(c_instance)

            if clas == 'Person.emotion':
                is_emotion = True
                emotion_instance, created = data_models.Emotion.objects.get_or_create(
                    label=ent['title']
                )
                emotions.append(emotion_instance)

        if not is_emotion:
            found_entities.append(entity_instance)

        data.entities.add(entity_instance)

    for entity in found_entities:
        for emotion in emotions:
            data_models.EmotionalEntity.objects.create(
                emotion=emotion, entity=entity, data=data)

    aspects = {}
    if request.POST.get('aspect_model'):
        aspects = requests.post('{HOST}/v4/{APIKEY}/aspect.json'.format(
            HOST=settings.HOST, APIKEY=settings.APIKEY),
            {'text': text, 'neutral': 1, 'lang': lang, 'model': request.POST['aspect_model']}).json()

    for key, value in aspects.items():
        if key != "status":
            for v in value:
                data_models.Aspect.objects.create(
                    data=data,
                    label=key,
                    chunk=v['chunk'],
                    sentiment=v['score'],
                    topic=v['sentiment_topic'],
                    sentiment_text=v['sentiment_text']
                )

    return JsonResponse({"status": "OK"})


def export_card(request):
    pass
