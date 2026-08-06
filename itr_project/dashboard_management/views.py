from django.http import JsonResponse
from .models import Dashboard

def dashboard_home(request):
    total_users = Dashboard.objects.count()

    return JsonResponse({
        "status": "success",
        "module": "User Dashboard Management",
        "total_users": total_users
    })