from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
import requests

from .permissions import IsAllowedAccessToData
import data.models as data_models
from data import serializers
from data import weighted

class DataViewSet(viewsets.ModelViewSet):
    queryset = data_models.Data.objects.all()
    serializer_class = serializers.DataSerializer
    permission_classes = [IsAllowedAccessToData]

country_param = openapi.Parameter('country', in_=openapi.IN_QUERY, description='Filter By Country',
                                   type=openapi.TYPE_STRING)
source_param = openapi.Parameter('source', in_=openapi.IN_QUERY, description='Filter By Source',
                                   type=openapi.TYPE_STRING)
language_param = openapi.Parameter('language', in_=openapi.IN_QUERY, description='Filter By Language',
                                   type=openapi.TYPE_STRING)
date_created_param = openapi.Parameter('date_created',
                                       in_=openapi.IN_QUERY,
                                       description='Filter By Created Period. Example: :start_date,:end_date. Here '
                                                   'start_date and end_date can be empty'
                                       , type=openapi.TYPE_STRING)


class ProjectDataListView(ListAPIView):
    serializer_class = serializers.DataSerializer
    permission_classes = [IsAllowedAccessToData]

    def get_queryset(self):
        filters = {
            'project_id': self.request.parser_context.get('kwargs', {}).get('project_id')
        }

        if self.request.query_params.get('country'):
            filters['country__label'] = self.request.query_params.get('country');

        if self.request.query_params.get('source'):
            filters['source__label'] = self.request.query_params.get('source')

        if self.request.query_params.get('date_created'):
            start_date, end_date = self.request.query_params.get('date_created').split(',')

            if start_date:
                filters['date_created__gt'] = start_date
            if end_date:
                filters['date_created__lt'] = end_date

        if self.request.query_params.get('language'):
            filters['language'] = self.request.query_params.get('language')

        return data_models.Data.objects.filter(**filters)

    @swagger_auto_schema(manual_parameters=[country_param, source_param, language_param, date_created_param])
    def get(self, request, *args, **kwargs):
        return super(ProjectDataListView, self).get(request, *args, **kwargs)


class SourceListAPI(ListAPIView):
    queryset = data_models.Source.objects.all()
    serializer_class = serializers.SourceSerializer

class CountryListAPI(ListAPIView):
    queryset = data_models.Country.objects.all()
    serializer_class = serializers.CountrySerializer

class ProjectListView(ListAPIView):
    serializer_class = serializers.ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return data_models.Project.objects.filter(users=self.request.user)

@csrf_exempt
def create_project(request):
    """
    API endpoint for creating a project. May need some work as we go.

    `name`: the name of the Project. If it doesn't exist, create it.
    `username`: the user name to add to this project. User is assumed to exist.
    `aspect_model`: the aspect model this project will use.
    """
    if 'name' not in request.POST or 'username' not in request.POST:
        return JsonResponse({"status": "Fail", "description": "Both `name` and `username` are required"})

    proj, _ = data_models.Project.objects.get_or_create(
        name=request.POST['name'])

    if 'aspect_model' in request.POST:
        m, _ = data_models.AspectModel.objects.get_or_create(label=request.POST['aspect_model'])
        proj.aspect_model = m
        proj.save()

    user, _ = User.objects.get_or_create(username=request.POST['username'])
    proj.users.add(user)

    return JsonResponse({"status": "OK", "project_id": proj.id})

@csrf_exempt
def add_data(request, project_id):
    """
    API endpoint for loading data. May need some work as we go.
    
    Required: 
        text: the text itself
        source: where did the text come from, create if doesn't exist

    Optional:
        country: the country this data came from
        with_entities=0/1: should we extract entities
        lang: language of the text
        url: URL of the original data source
        date: date this item was created, defaults today
        weight_type: the weighting formula to use
        weight_args: the arguments to supply to the weighting formula, varies
            based on weight_type. Supplied as a JSON string.
    """
    for key in ('text', 'source'):
        if key not in request.POST:
            return JsonResponse({
                "status": "Fail", 
                "message": "Missing required field `{}`".format(key)
            })
    
    text = request.POST['text']
    lang = request.POST.get('lang', 'en')

    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), data={'text': text, 'lang': lang}).json()
        if 'score' in resp:
            sentiment = resp['score']
        else:
            return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({"status": "Fail", "message": "Could not add text = {} lang = {} because: {}".format(text, lang, e)})
    
    project = data_models.Project.objects.get(pk=project_id)

    source, _ = data_models.Source.objects.get_or_create(
        label=request.POST['source'])

    weight_args = json.loads(request.POST.get('weight_args', '{}'))
    weight_args['raw_score'] = sentiment
    weighted_score = weighted.calculate(**weight_args)
    
    data = data_models.Data.objects.create(
        date_created=request.POST.get('date', datetime.datetime.now().date()),
        project=project,
        source=source,
        text=text,
        sentiment=sentiment,
        weighted_score=weighted_score,
        language=lang,
        url=requests.POST.get('url', ''),
    )
    
    if request.POST.get('country'):
        country, _ = data_models.Country.objects.get_or_create(
            label=request.POST['country'])
        data.country = country
        data.save()

    # Add keywords.
    for keyword, count in resp['keywords'].items():
        kw, _ = data_models.Keyword.objects.get_or_create(label=keyword)
        for i in range(count):
            data.keywords.add(kw)

    if request.POST.get('with_entities'):
        for ent in resp['entities']:
            entity_instance, created = data_models.Entity.objects.get_or_create(
                label=ent['title']
            )

            for clas in ent['classifications']:
                c_instance, created = data_models.Classification.objects.get_or_create(
                    label=clas
                )
                entity_instance.classifications.add(c_instance)

            data.entities.add(entity_instance)

    if project.aspect_model:
        aspects = requests.post('{HOST}/v4/{APIKEY}/aspect.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY),
            {'text': text, 'neutral': 1, 'lang': lang, 'model': project.aspect_model.label}).json()

        for key, value in aspects.items():
            if key != "status" and aspects['status'] == 'OK':
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
