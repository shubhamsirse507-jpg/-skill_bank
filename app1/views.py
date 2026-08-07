import uuid

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Doubt, Booking, Notification, VideoSession
from .forms import DoubtForm, BookingForm


def test_ui(request):
    try:
        return render(request, "app1/testing_ui.html")
    except Exception:
        return render(request, "testing_ui.html")


def home(request):
    if "text/html" in request.headers.get("Accept", ""):
        return test_ui(request)
    return JsonResponse({"message": "SkillBank Backend Running", "testing_ui": "/test_ui/"})


# Live Doubt Solving Module
@csrf_exempt
def add_doubt(request):
    if request.method == "POST":
        form = DoubtForm(request.POST, request.FILES)
        if form.is_valid():
            doubt = form.save()
            Notification.objects.create(message=f"New Doubt Added: {doubt.title}")
            return JsonResponse({"status": "Doubt Added Successfully", "id": doubt.id})
        return JsonResponse(form.errors, status=400)

    return JsonResponse({"message": "Send POST request to add doubt"})


def view_doubt(request):
    doubts = Doubt.objects.all().order_by('-id').values()
    return JsonResponse(list(doubts), safe=False)


# Booking Module
@csrf_exempt
def book_session(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            Notification.objects.create(message=f"Session Booked: {booking.student_name} with {booking.teacher_name}")
            return JsonResponse({"status": "Session Booked", "id": booking.id})
        return JsonResponse(form.errors, status=400)

    return JsonResponse({"message": "Send POST request to book session"})


def booking_list(request):
    bookings = Booking.objects.all().order_by('-id').values()
    return JsonResponse(list(bookings), safe=False)


# Notification Module
def notifications(request):
    notification = Notification.objects.all().order_by('-id').values()
    return JsonResponse(list(notification), safe=False)


# Video Meeting
@csrf_exempt
def create_meeting(request):
    booking = Booking.objects.last()

    if booking is None:
        return JsonResponse({
            "error": "No booking found. Please create a booking first."
        }, status=400)

    meeting_id = str(uuid.uuid4())[:8]

    session = VideoSession.objects.create(
        booking=booking,
        student_name=booking.student_name,
        teacher_name=booking.teacher_name,
        meeting_id=meeting_id,
        meeting_link=f"https://meet.jit.si/SkillBank_{meeting_id}"
    )

    return JsonResponse({
        "student": booking.student_name,
        "teacher_name": booking.teacher_name,
        "meeting_id": session.meeting_id,
        "meeting_link": session.meeting_link,
        "status": "Meeting Created"
    })