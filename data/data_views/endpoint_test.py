from django.http import HttpResponse
from dashboard.tasks import process_data

def endpoint_test(request):
    process_data.delay({"text":"this food is good", "lang":"en", "project_id":3232})
    return HttpResponse("endpoint test")