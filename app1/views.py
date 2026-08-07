import uuid

from django.http import JsonResponse
from .models import Doubt, Booking, Notification, VideoSession
from .forms import DoubtForm, BookingForm


def home(request):
    return JsonResponse({"message": "SkillBank Backend Running"})


# Live Doubt Solving Module
def add_doubt(request):
    if request.method == "POST":
        form = DoubtForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            Notification.objects.create(message="New Doubt Added")
            return JsonResponse({"status": "Doubt Added Successfully"})
        return JsonResponse(form.errors)

    return JsonResponse({"message": "Send POST request to add doubt"})


def view_doubt(request):
    doubts = Doubt.objects.all().values()
    return JsonResponse(list(doubts), safe=False)


# Booking Module
def book_session(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            Notification.objects.create(message="Session Booked Successfully")
            return JsonResponse({"status": "Session Booked"})
        return JsonResponse(form.errors)

    return JsonResponse({"message": "Send POST request to book session"})


def booking_list(request):
    bookings = Booking.objects.all().values()
    return JsonResponse(list(bookings), safe=False)


# Notification Module
def notifications(request):
    notification = Notification.objects.all().values()
    return JsonResponse(list(notification), safe=False)


# Video Meeting
def create_meeting(request):

    booking = Booking.objects.first()

    if booking is None:
        return JsonResponse({
            "error": "No booking found"
        })

    meeting_id = str(uuid.uuid4())[:8]

    session = VideoSession.objects.create(
        booking=booking,
        meeting_id=meeting_id,
        meeting_link=f"https://meet.jit.si/{meeting_id}"
    )

    return JsonResponse({
        "student": booking.student_name,
        "mentor": booking.mentor_name,
        "meeting_id": session.meeting_id,
        "meeting_link": session.meeting_link,
        "status": "Meeting Created"
    })