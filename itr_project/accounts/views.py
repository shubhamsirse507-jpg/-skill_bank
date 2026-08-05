import json
import random

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from .models import User

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            email = data.get("email")
            password = data.get("password")

            user = User.objects.get(email=email)

            if user.password == password:
                return JsonResponse({
                    "status": "success",
                    "message": "Login Successful"
                })
            else:
                return JsonResponse({
                    "status": "failed",
                    "message": "Invalid Password"
                })

        except User.DoesNotExist:
            return JsonResponse({
                "status": "failed",
                "message": "Email Not Found"
            })

    return JsonResponse({
        "message": "Only POST method is allowed"
    })


@csrf_exempt
def forgot_password(request):

    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")

        try:
            user = User.objects.get(email=email)

            otp = str(random.randint(100000, 999999))

            user.otp = otp
            user.save()

            send_mail(
                subject="Skill Bank OTP",
                message=f"Your OTP is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({
                "status": "success",
                "message": "OTP sent successfully"
            })

        except User.DoesNotExist:
            return JsonResponse({
                "status": "failed",
                "message": "Email not registered"
            })

    return JsonResponse({
        "status": "failed",
        "message": "Only POST request allowed"
    })


@csrf_exempt
def verify_otp(request):
    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        otp = data.get("otp")

        try:
            user = User.objects.get(email=email)

            if user.otp == otp:
                return JsonResponse({
                    "status": "success",
                    "message": "OTP Verified"
                })

            return JsonResponse({
                "status": "failed",
                "message": "Invalid OTP"
            })

        except User.DoesNotExist:
            return JsonResponse({
                "status": "failed",
                "message": "User Not Found"
            })

    return JsonResponse({
        "message": "Only POST method is allowed"
    })

@csrf_exempt
def reset_password(request):
    if request.method == "POST":

        data = json.loads(request.body)

        email = data.get("email")
        new_password = data.get("password")

        try:
            user = User.objects.get(email=email)

            user.password = new_password
            user.otp = ""
            user.save()

            return JsonResponse({
                "status": "success",
                "message": "Password Reset Successful"
            })

        except User.DoesNotExist:
            return JsonResponse({
                "status": "failed",
                "message": "User Not Found"
            })

    return JsonResponse({
        "message": "Only POST method is allowed"
    })