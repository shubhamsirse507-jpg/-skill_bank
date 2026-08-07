from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)

            if user.password == password:
                return JsonResponse({
                    "status": "success",
                    "message": "Login Successful"
                })

            return JsonResponse({
                "status": "failed",
                "message": "Invalid Password"
            })

        except User.DoesNotExist:
            return JsonResponse({
                "status": "failed",
                "message": "Email not found"
            })

    return JsonResponse({
        "message": "Only POST request allowed"
    })