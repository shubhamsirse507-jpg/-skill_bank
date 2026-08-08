"""
authentication/views.py
Functional Authentication module:
- Login (session-based)
- Register (creates auth.User + UserProfile)
- Logout
- Forgot Password (generates OTP using OTPVerification model)
- Verify OTP
- Reset Password
"""

import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from authentication.constants import AUTH_BACKGROUND_VIDEO_URL, BRAND_LOGO_IMAGE_NAME
from authentication.models import OTPVerification
from profiles.models import UserProfile


def landing(request):
    """Public landing page — root URL."""
    return render(request, 'authentication/landing.html')


def login(request):
    """Handles GET and POST for User Login."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username_or_email or not password:
            messages.error(request, 'Please provide both username/email and password.')
            return render(request, 'authentication/login.html', {
                'error': 'Please provide both username/email and password.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        # Allow login by email or username
        user_obj = User.objects.filter(email__iexact=username_or_email).first()
        username = user_obj.username if user_obj else username_or_email

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account has been suspended or deactivated.')
                return render(request, 'authentication/login.html', {
                    'error': 'Your account has been suspended or deactivated.',
                    'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                    'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
                })
            
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next') or request.POST.get('next')
            if not next_url or next_url == 'user_dashboard':
                next_url = 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username/email or password.')
            return render(request, 'authentication/login.html', {
                'error': 'Invalid username/email or password.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

    return render(request, 'authentication/login.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })


def register(request):
    """Handles GET and POST for User Registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        fullname = request.POST.get('fullname', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'user').strip()

        if fullname and not (first_name or last_name):
            parts = fullname.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        if not confirm_password:
            confirm_password = password

        if not username or not email or not password:
            messages.error(request, 'Username, email, and password are required.')
            return render(request, 'authentication/login.html', {
                'error': 'Username, email, and password are required.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/login.html', {
                'error': 'Passwords do not match.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'authentication/login.html', {
                'error': 'Username is already taken.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'authentication/login.html', {
                'error': 'An account with this email already exists.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create linked UserProfile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            status='active',
            role=role if role in ['user', 'student', 'teacher', 'admin'] else 'user'
        )

        # Auto login
        auth_login(request, user)
        messages.success(request, f'Account created successfully! Welcome, {user.first_name or user.username}!')
        return redirect('home')

    return render(request, 'authentication/register.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })


@login_required
def logout_view(request):
    """Logs out the user."""
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def forgot_password(request):
    """Generates 6-digit OTP and sends via email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return redirect('forgot_password')

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, 'No account found with that email address.')
            return redirect('forgot_password')

        # Generate & store OTP model record
        otp = str(random.randint(100000, 999999))
        expires = timezone.now() + timedelta(minutes=10)

        OTPVerification.objects.create(
            user=user,
            otp_code=otp,
            purpose='ForgotPassword',
            expires_at=expires
        )

        request.session['otp_email'] = email
        request.session['otp_user_id'] = user.id

        # Send email
        try:
            send_mail(
                subject='Your Skill Bank Password Reset OTP',
                message=f'Hello {user.first_name or user.username},\n\nYour OTP code for password reset is: {otp}\n\nThis code expires in 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f'OTP sent to {email}')
        return redirect('verify_otp')

    return render(request, 'authentication/forgot_password.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
    })


def verify_otp(request):
    """Verifies submitted OTP against OTPVerification model."""
    email = request.session.get('otp_email', '')
    user_id = request.session.get('otp_user_id')

    if request.method == 'POST':
        submitted_otp = request.POST.get('otp', '').strip()
        if not user_id:
            messages.error(request, 'Session expired. Please request a new OTP.')
            return redirect('forgot_password')

        otp_record = OTPVerification.objects.filter(
            user_id=user_id,
            otp_code=submitted_otp,
            purpose='ForgotPassword',
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, 'Invalid OTP code. Please check and try again.')
        elif otp_record.is_expired():
            messages.error(request, 'OTP has expired. Please request a new one.')
        else:
            otp_record.is_verified = True
            otp_record.save()
            request.session['otp_verified_user_id'] = user_id
            messages.success(request, 'OTP verified! Set your new password.')
            return redirect('reset_password')

    return render(request, 'authentication/otp.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
        'email': email,
    })


def reset_password(request):
    """Renders new password page and updates user password after OTP verification."""
    user_id = request.session.get('otp_verified_user_id')
    if not user_id:
        messages.error(request, 'Unauthorized. Please verify your OTP first.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not password or password != confirm_password:
            messages.error(request, 'Passwords do not match or are empty.')
            return render(request, 'authentication/reset_password.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        user = User.objects.filter(id=user_id).first()
        if user:
            user.set_password(password)
            user.save()
            # Cleanup session
            request.session.pop('otp_email', None)
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_verified_user_id', None)

            messages.success(request, 'Password updated successfully! Please log in.')
            return redirect('login')

    return render(request, 'authentication/reset_password.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })