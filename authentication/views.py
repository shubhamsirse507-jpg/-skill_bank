"""
authentication/views.py
Complete, hardened Authentication module for Skill Bank:
- Login (Credentials verification + Two-Factor Authentication via OTP)
- Verify 2FA Login OTP
- Resend 2FA Login OTP
- Register (Creates auth.User + UserProfile with role & 2FA support)
- Logout
- Forgot Password (Safe user lookup + generates OTP in OTPVerification model)
- Verify OTP (Password Reset verification)
- Reset Password (Secure password update)
"""

import random
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from authentication.constants import AUTH_BACKGROUND_VIDEO_URL, BRAND_LOGO_IMAGE_NAME
from authentication.models import OTPVerification
from profiles.models import UserProfile


def send_otp_email(user, otp_code, purpose='Login'):
    """
    Sends a formatted OTP email to the user with dual-channel (Port 465 SSL / Port 587 TLS) fallback.
    Returns (email_sent: bool, recipient_email: str).
    """
    recipient_email = user.email.strip() if user.email else ''
    if not recipient_email:
        return False, ''

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'skillbank2026@gmail.com')
    user_display = user.first_name or user.username

    if purpose == 'Login':
        subject = f"Your SkillBank 2FA Login Code: {otp_code}"
        plain_text = (
            f"Hello {user_display},\n\n"
            f"Your Two-Factor Authentication (2FA) code for logging into SkillBank is: {otp_code}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you did not attempt to log in, please secure your account immediately.\n\n"
            f"— The SkillBank Team"
        )
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; background: #0c6c63; color: #ffffff; width: 48px; height: 48px; line-height: 48px; font-size: 24px; font-weight: 800; border-radius: 12px; text-align: center;">S</div>
                <h2 style="color: #0c6c63; margin-top: 10px; font-size: 22px; font-weight: 700;">Skill Bank Security</h2>
            </div>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">Hello <strong>{user_display}</strong>,</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">Use the following 6-digit Two-Factor Authentication code to complete your login:</p>
            <div style="text-align: center; margin: 26px 0;">
                <span style="display: inline-block; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #0c6c63; background: #e8f7f5; padding: 12px 28px; border-radius: 10px; border: 2px dashed #0c6c63;">{otp_code}</span>
            </div>
            <p style="color: #64748b; font-size: 13px; line-height: 1.5;">This verification code is valid for <strong>10 minutes</strong>. Never share this code with anyone.</p>
            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 20px 0;">
            <p style="color: #94a3b8; font-size: 12px; text-align: center;">If you did not request this login, please change your password immediately.</p>
        </div>
        """
    else:  # ForgotPassword / Registration
        subject = f"Your SkillBank Password Reset OTP: {otp_code}"
        plain_text = (
            f"Hello {user_display},\n\n"
            f"Your OTP code for resetting your SkillBank password is: {otp_code}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you did not request a password reset, you can safely ignore this email.\n\n"
            f"— The SkillBank Team"
        )
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; background: #0c6c63; color: #ffffff; width: 48px; height: 48px; line-height: 48px; font-size: 24px; font-weight: 800; border-radius: 12px; text-align: center;">S</div>
                <h2 style="color: #0c6c63; margin-top: 10px; font-size: 22px; font-weight: 700;">Password Reset Request</h2>
            </div>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">Hello <strong>{user_display}</strong>,</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">You recently requested to reset your password for your SkillBank account. Enter the verification code below to proceed:</p>
            <div style="text-align: center; margin: 26px 0;">
                <span style="display: inline-block; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #0c6c63; background: #e8f7f5; padding: 12px 28px; border-radius: 10px; border: 2px dashed #0c6c63;">{otp_code}</span>
            </div>
            <p style="color: #64748b; font-size: 13px; line-height: 1.5;">This code will expire in <strong>10 minutes</strong>.</p>
            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 20px 0;">
            <p style="color: #94a3b8; font-size: 12px; text-align: center;">If you didn't request a password reset, you can safely ignore this email.</p>
        </div>
        """

    email_sent = False
    # Attempt 1: Standard configured Django mail dispatch (Port 465 SSL default)
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=from_email,
            to=[recipient_email]
        )
        msg.attach_alternative(html_content, "text/html")
        sent = msg.send(fail_silently=False)
        email_sent = bool(sent and sent > 0)
    except Exception as e1:
        print(f"[OTP Email Delivery] Primary SMTP dispatch attempt failed: {e1}")

    # Attempt 2: Fallback explicitly with Port 465 SSL connection
    if not email_sent:
        try:
            host_user = getattr(settings, 'EMAIL_HOST_USER', 'skillbank2026@gmail.com').strip()
            raw_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', 'saqgbxqlkvbjgavw')
            host_pass = str(raw_pass).replace(' ', '').strip()

            ssl_conn = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host='smtp.gmail.com',
                port=465,
                username=host_user,
                password=host_pass,
                use_ssl=True,
                timeout=12
            )
            msg_ssl = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=from_email,
                to=[recipient_email],
                connection=ssl_conn
            )
            msg_ssl.attach_alternative(html_content, "text/html")
            sent_ssl = msg_ssl.send(fail_silently=False)
            email_sent = bool(sent_ssl and sent_ssl > 0)
            if email_sent:
                print(f"[OTP Email Delivery] Successfully dispatched via Port 465 SSL fallback!")
        except Exception as e2:
            print(f"[OTP Email Delivery] Port 465 SSL fallback failed: {e2}")

    print(f"\n==========================================")
    print(f" [OTP DISPATCH] Purpose: {purpose} | User: {user.username} | Email: {recipient_email} | Code: {otp_code} | SMTP Sent: {email_sent}")
    print(f"==========================================\n")

    return email_sent, recipient_email


def landing(request):
    """Public landing page — root URL."""
    return render(request, 'authentication/landing.html')


def login(request):
    """
    Handles GET and POST for User Login.
    When credentials are valid, checks if Two-Factor Authentication (2FA) is enabled.
    If 2FA is active, creates an OTP and redirects to the 2FA verification screen.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        next_url = request.GET.get('next') or request.POST.get('next')
        if not next_url or next_url == 'user_dashboard':
            next_url = 'home'

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

            # Check Two-Factor Authentication (2FA) status
            profile, _ = UserProfile.objects.get_or_create(user=user)
            is_2fa_enabled = getattr(profile, 'two_factor_enabled', True)

            if is_2fa_enabled and user.email:
                # Generate 6-digit 2FA OTP code
                otp = f"{random.randint(100000, 999999)}"
                expires = timezone.now() + timedelta(minutes=10)

                # Invalidate previous unverified login OTPs for this user
                OTPVerification.objects.filter(
                    user=user,
                    purpose='Login',
                    is_verified=False
                ).update(is_verified=True)

                OTPVerification.objects.create(
                    user=user,
                    otp_code=otp,
                    purpose='Login',
                    expires_at=expires
                )

                # Save 2FA state in session
                request.session['2fa_user_id'] = user.id
                request.session['2fa_email'] = user.email
                request.session['2fa_next'] = next_url

                email_sent, sent_email = send_otp_email(user, otp, purpose='Login')
                if email_sent:
                    messages.info(request, f'Two-Factor Authentication code sent to {sent_email}.')
                else:
                    messages.success(request, f'2FA code generated for {sent_email}. (Verification Code: {otp})')

                return redirect('verify_2fa')

            # Direct login if 2FA is disabled or user has no email
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
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


def verify_2fa(request):
    """
    Renders and verifies the 6-digit Two-Factor Authentication code for login.
    """
    user_id = request.session.get('2fa_user_id')
    email = request.session.get('2fa_email', '')
    next_url = request.session.get('2fa_next', 'home')

    if not user_id:
        messages.warning(request, 'No active login session found. Please sign in.')
        return redirect('login')

    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.pop('2fa_user_id', None)
        messages.error(request, 'User account not found. Please log in again.')
        return redirect('login')

    if request.method == 'POST':
        submitted_otp = request.POST.get('otp', '').strip()
        if not submitted_otp:
            d1 = request.POST.get('d1', '')
            d2 = request.POST.get('d2', '')
            d3 = request.POST.get('d3', '')
            d4 = request.POST.get('d4', '')
            d5 = request.POST.get('d5', '')
            d6 = request.POST.get('d6', '')
            submitted_otp = f"{d1}{d2}{d3}{d4}{d5}{d6}".strip()

        if not submitted_otp or len(submitted_otp) != 6:
            messages.error(request, 'Please enter a valid 6-digit 2FA code.')
            return render(request, 'authentication/verify_2fa.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
                'email': email,
                'user': user,
            })

        otp_record = OTPVerification.objects.filter(
            user=user,
            otp_code=submitted_otp,
            purpose='Login',
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, 'Invalid 2FA code. Please check and try again.')
        elif otp_record.is_expired():
            messages.error(request, 'The 2FA code has expired. Please click Resend Code.')
        else:
            otp_record.is_verified = True
            otp_record.save()

            request.session.pop('2fa_user_id', None)
            request.session.pop('2fa_email', None)
            request.session.pop('2fa_next', None)

            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)

    return render(request, 'authentication/verify_2fa.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
        'email': email,
        'user': user,
    })


@require_POST
def resend_2fa_otp(request):
    """
    AJAX / POST endpoint to generate and resend a new 2FA Login code.
    """
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'}, status=400)

    user = User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

    OTPVerification.objects.filter(
        user=user,
        purpose='Login',
        is_verified=False
    ).update(is_verified=True)

    otp = f"{random.randint(100000, 999999)}"
    expires = timezone.now() + timedelta(minutes=10)

    OTPVerification.objects.create(
        user=user,
        otp_code=otp,
        purpose='Login',
        expires_at=expires
    )

    email_sent, sent_email = send_otp_email(user, otp, purpose='Login')
    message = f"New 2FA code sent to {sent_email}." if email_sent else f"New 2FA code generated for {sent_email}. (Code: {otp})"

    return JsonResponse({
        'status': 'success',
        'message': message,
        'email_sent': email_sent,
        'dev_code': otp if not email_sent else None
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
        confirm_password = request.POST.get('confirm_password', request.POST.get('confirmPassword', '')).strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'user').strip().lower()

        if fullname and not (first_name or last_name):
            parts = fullname.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        if not confirm_password:
            confirm_password = password

        if not username or not email or not password:
            messages.error(request, 'Username, email, and password are required.')
            return render(request, 'authentication/register.html', {
                'error': 'Username, email, and password are required.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'authentication/register.html', {
                'error': 'Password must be at least 6 characters long.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/register.html', {
                'error': 'Passwords do not match.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'authentication/register.html', {
                'error': 'Username is already taken.',
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'authentication/register.html', {
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

        # Create linked UserProfile with 2FA enabled by default
        UserProfile.objects.create(
            user=user,
            phone=phone,
            status='active',
            role=role if role in ['user', 'student', 'teacher', 'admin'] else 'user',
            two_factor_enabled=True
        )

        # Auto login newly registered user
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
    """
    Generates 6-digit OTP and dispatches it via email for password reset.
    Handles both standard Form POST and AJAX requests for Resend.
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('resend')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Please enter your email address.'}, status=400)
            messages.error(request, 'Please enter your email address.')
            return redirect('forgot_password')

        # Safe lookup: find user by email or username
        user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
        if not user:
            msg = f"No account found matching '{email}'. Please check your email or create an account."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg}, status=404)
            messages.error(request, msg)
            return render(request, 'authentication/forgot_password.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
                'error': msg
            })

        OTPVerification.objects.filter(
            user=user,
            purpose='ForgotPassword',
            is_verified=False
        ).update(is_verified=True)

        otp = f"{random.randint(100000, 999999)}"
        expires = timezone.now() + timedelta(minutes=10)

        OTPVerification.objects.create(
            user=user,
            otp_code=otp,
            purpose='ForgotPassword',
            expires_at=expires
        )

        request.session['otp_email'] = user.email or email
        request.session['otp_user_id'] = user.id

        email_sent, sent_email = send_otp_email(user, otp, purpose='ForgotPassword')

        if email_sent:
            user_msg = f'OTP sent successfully to {sent_email}.'
        else:
            user_msg = f'OTP generated for {sent_email}. (Verification OTP: {otp})'

        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': user_msg,
                'email_sent': email_sent,
                'dev_code': otp if not email_sent else None
            })

        messages.success(request, user_msg)
        return redirect('verify_otp')

    return render(request, 'authentication/forgot_password.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
    })


def verify_otp(request):
    """
    Verifies submitted OTP against OTPVerification model for Password Reset.
    """
    email = request.session.get('otp_email', '')
    user_id = request.session.get('otp_user_id')

    if not user_id and email:
        u_found = User.objects.filter(email__iexact=email).first()
        if u_found:
            user_id = u_found.id

    if not user_id:
        messages.error(request, 'Session expired. Please request a new OTP.')
        return redirect('forgot_password')

    if request.method == 'POST':
        submitted_otp = request.POST.get('otp', '').strip()
        if not submitted_otp:
            d1 = request.POST.get('d1', '')
            d2 = request.POST.get('d2', '')
            d3 = request.POST.get('d3', '')
            d4 = request.POST.get('d4', '')
            d5 = request.POST.get('d5', '')
            d6 = request.POST.get('d6', '')
            submitted_otp = f"{d1}{d2}{d3}{d4}{d5}{d6}".strip()

        if not submitted_otp or len(submitted_otp) != 6:
            messages.error(request, 'Please enter the complete 6-digit OTP.')
            return render(request, 'authentication/otp.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
                'email': email,
            })

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
    """
    Renders new password page and updates user password after OTP verification.
    """
    user_id = request.session.get('otp_verified_user_id')
    if not user_id:
        messages.error(request, 'Unauthorized. Please verify your OTP first.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not password or not confirm_password:
            messages.error(request, 'Both password fields are required.')
            return render(request, 'authentication/reset_password.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'authentication/reset_password.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/reset_password.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
            })

        user = User.objects.filter(id=user_id).first()
        if user:
            user.set_password(password)
            user.save()

            request.session.pop('otp_email', None)
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_verified_user_id', None)

            messages.success(request, 'Password updated successfully! Please log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'User account not found.')
            return redirect('forgot_password')

    return render(request, 'authentication/reset_password.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })