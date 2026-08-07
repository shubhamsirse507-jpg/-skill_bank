import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from authentication.constants import AUTH_BACKGROUND_VIDEO_URL, BRAND_LOGO_IMAGE_NAME


def landing(request):
    """Public landing page — shown at the root URL."""
    return render(request, 'authentication/landing.html')


def login(request):
    return render(request, 'authentication/login.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })


def register(request):
    return render(request, 'authentication/register.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })


def forgot_password(request):
    """
    GET  – Show the forgot-password form.
    POST – Generate a 6-digit OTP, store it in the session, e-mail it
           to the user, then redirect to the OTP verification page.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return redirect('forgot_password')

        # Check the user exists (optional – remove if you don't want to leak info)
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No account found with that email address.')
            return redirect('forgot_password')

        # Generate & store OTP
        otp = str(random.randint(100000, 999999))
        request.session['otp']       = otp
        request.session['otp_email'] = email

        # Send OTP email
        try:
            send_mail(
                subject='Your Skill Bank Password Reset OTP',
                message=f'Your OTP code is: {otp}\n\nThis code expires in 2 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            messages.error(request, 'Failed to send OTP email. Please try again.')
            return redirect('forgot_password')

        messages.success(request, f'OTP sent to {email}')
        return redirect('verify_otp')

    return render(request, 'authentication/forgot_password.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
    })


def verify_otp(request):
    """
    GET  – Show the OTP entry form (requires an active OTP session).
    POST – Compare submitted OTP with the one stored in the session.
           On success: clear OTP from session and redirect to login (or
           a password-reset page if your team has built one).
    """
    email = request.session.get('otp_email', '')

    if request.method == 'POST':
        submitted_otp = request.POST.get('otp', '').strip()
        stored_otp    = request.session.get('otp', '')

        if not stored_otp:
            messages.error(request, 'OTP has expired or was never sent. Please try again.')
            return redirect('forgot_password')

        if submitted_otp == stored_otp:
            # OTP is correct – clean up session
            del request.session['otp']
            del request.session['otp_email']

            messages.success(request, 'OTP verified successfully!')
            # TODO: redirect to a set-new-password page once your team builds it
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please check the code and try again.')

    return render(request, 'authentication/otp.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
        'email': email,
    })

