from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import data.models as data_models
from dashboard.tasks import process_data


@method_decorator(csrf_exempt, name='dispatch')
class DataItems(View):

    @method_decorator(login_required)
    def put(self, request):
        data_items_id = request.GET.get("data-items")
        if data_items_id != "":
            data_items_id = data_items_id.split(",")
        else:
            data_items_id = []
        for data_id in data_items_id:
            data_item = get_object_or_404(data_models.Data,
                                          pk=data_id,
                                          project__users=request.user)
            if data_item:
                process_data.delay({"data_id": data_item.id})
        return HttpResponse()
