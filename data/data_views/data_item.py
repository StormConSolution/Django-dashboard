from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import data.models as data_models
from dashboard.tasks import process_data


@method_decorator(csrf_exempt, name='dispatch')
class DataItem(View):

    @method_decorator(login_required)
    def get(self, request, data_id):
        data_item = get_object_or_404(data_models.Data,
                                      pk=data_id,
                                      project__users=request.user)

        return JsonResponse({
            "id": data_item.id,
            "text": data_item.text,
            "date_created": data_item.date_created,
            "language": data_item.language,
            "source": {
                "id": data_item.source.id,
                "label": data_item.source.label,
            },
            "sentiment": data_item.sentiment,

        })

    @method_decorator(login_required)
    def delete(self, request, data_id):
        data_item = get_object_or_404(data_models.Data,
                                      pk=data_id,
                                      project__users=request.user)
        data_item.delete()
        return HttpResponse()

    @method_decorator(login_required)
    def put(self, request, data_id):
        data_item = get_object_or_404(data_models.Data,
                                      pk=data_id,
                                      project__users=request.user)
        process_data.delay({"data_id": data_item.id})
        return HttpResponse()

    @method_decorator(login_required)
    def post(self, request, data_id):
        new_text = request.POST.get("text")
        new_language = request.POST.get("language")
        new_sentiment = request.POST.get("sentiment")
        data_item = get_object_or_404(data_models.Data,
                                      pk=data_id,
                                      project__users=request.user)
        data_item.text = new_text
        data_item.language = new_language
        data_item.sentiment = new_sentiment
        data_item.save()
        # process_data.delay({"data_id": data_item.id})
        return HttpResponse()
