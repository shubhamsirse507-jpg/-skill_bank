from django.http import JsonResponse
from .models import Dashboard

def dashboard_view(request):
    data = Dashboard.objects.all().values()

    return JsonResponse({
        "status": "success",
        "data": list(data)
    })