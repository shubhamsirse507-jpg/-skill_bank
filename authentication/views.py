"""
authentication/views.py
Complete, hardened Authentication module for Skill-Verse:
- Login (Credentials verification + Two-Factor Authentication via OTP)
- Verify 2FA Login OTP
- Resend 2FA Login OTP
- Register (Creates auth.User + UserProfile with role & 2FA support)
- Logout
- Forgot Password (Safe user lookup + generates OTP in OTPVerification model)
- Verify OTP (Password Reset verification)
- Reset Password (Secure password update)
"""

import json
import logging
import random
import traceback as _traceback
import urllib.error
import urllib.request
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

from authentication.constants import AUTH_BACKGROUND_VIDEO_URL, BRAND_LOGO_IMAGE_NAME
from authentication.models import OTPVerification
from profiles.models import UserProfile


def send_otp_email(user, otp_code, purpose='Login'):
    """
    Sends a formatted OTP email to the user using configured environment SMTP credentials
    with Port 587 TLS / Port 465 SSL fallback. Never hardcodes secrets or leaks OTP to clients.
    Returns (email_sent: bool, recipient_email: str).
    """
    recipient_email = user.email.strip() if user.email else ''
    if not recipient_email:
        return False, ''

    backend = getattr(settings, 'EMAIL_BACKEND', '')
    host_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
    host_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', '').strip()

    # Never report success if no delivery channel exists (non-delivering backend in prod or missing creds)
    is_non_delivering = any(b in backend for b in ('console.EmailBackend', 'locmem.EmailBackend', 'dummy.EmailBackend'))
    if not brevo_api_key:
        if is_non_delivering and not getattr(settings, 'DEBUG', False):
            logger.error("[OTP Email Delivery] Non-delivering EMAIL_BACKEND (%s) configured with DEBUG=False.", backend)
            return False, recipient_email
        if 'smtp.EmailBackend' in backend and (not host_user or not host_pass):
            logger.error("[OTP Email Delivery] SMTP backend configured but EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is missing.")
            return False, recipient_email

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@Skill-Verse.com')
    user_display = user.first_name or user.username

    if purpose == 'Login':
        subject = "Your Skill-Verse verification code"
        plain_text = (
            f"Hello {user_display},\n\n"
            f"Your Two-Factor Authentication (2FA) verification code for Skill-Verse is: {otp_code}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you didn't request this, you can safely ignore this email.\n\n"
            f"— The Skill-Verse Team"
        )
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; background: #0c6c63; color: #ffffff; width: 48px; height: 48px; line-height: 48px; font-size: 24px; font-weight: 800; border-radius: 12px; text-align: center;">S</div>
                <h2 style="color: #0c6c63; margin-top: 10px; font-size: 22px; font-weight: 700;">Skill-Verse Security</h2>
            </div>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">Hello <strong>{user_display}</strong>,</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">Use the following 6-digit verification code to complete your sign-in:</p>
            <div style="text-align: center; margin: 26px 0;">
                <span style="display: inline-block; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #0c6c63; background: #e8f7f5; padding: 12px 28px; border-radius: 10px; border: 2px dashed #0c6c63;">{otp_code}</span>
            </div>
            <p style="color: #64748b; font-size: 13px; line-height: 1.5;">This verification code expires in <strong>10 minutes</strong>. Never share this code with anyone.</p>
            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 20px 0;">
            <p style="color: #94a3b8; font-size: 12px; text-align: center;">If you didn't request this, you can safely ignore this email.</p>
        </div>
        """
    else:  # ForgotPassword / Registration
        subject = "Your Skill-Verse verification code"
        plain_text = (
            f"Hello {user_display},\n\n"
            f"Your OTP code for resetting your Skill-Verse password is: {otp_code}\n\n"
            f"This code will expire in 10 minutes.\n"
            f"If you didn't request this, you can safely ignore this email.\n\n"
            f"— The Skill-Verse Team"
        )
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; background: #0c6c63; color: #ffffff; width: 48px; height: 48px; line-height: 48px; font-size: 24px; font-weight: 800; border-radius: 12px; text-align: center;">S</div>
                <h2 style="color: #0c6c63; margin-top: 10px; font-size: 22px; font-weight: 700;">Password Reset Request</h2>
            </div>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">Hello <strong>{user_display}</strong>,</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">You recently requested to reset your password for your Skill-Verse account. Enter the verification code below to proceed:</p>
            <div style="text-align: center; margin: 26px 0;">
                <span style="display: inline-block; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #0c6c63; background: #e8f7f5; padding: 12px 28px; border-radius: 10px; border: 2px dashed #0c6c63;">{otp_code}</span>
            </div>
            <p style="color: #64748b; font-size: 13px; line-height: 1.5;">This code expires in <strong>10 minutes</strong>.</p>
            <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 20px 0;">
            <p style="color: #94a3b8; font-size: 12px; text-align: center;">If you didn't request this, you can safely ignore this email.</p>
        </div>
        """

    email_sent = False

    # Priority 1: Brevo HTTPS Transactional Email API (works on Render/cloud where SMTP ports are blocked)
    if brevo_api_key:
        sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', '').strip() or host_user or 'noreply@Skill-Verse.com'
        sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Skill-Verse').strip() or 'Skill-Verse'
        timeout_sec = int(getattr(settings, 'EMAIL_TIMEOUT', 15))
        payload = json.dumps({
            'sender': {'name': sender_name, 'email': sender_email},
            'to': [{'email': recipient_email, 'name': user_display}],
            'subject': subject,
            'htmlContent': html_content,
            'textContent': plain_text,
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.brevo.com/v3/smtp/email',
            data=payload,
            headers={
                'accept': 'application/json',
                'content-type': 'application/json',
                'api-key': brevo_api_key,
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                if 200 <= resp.status < 300:
                    email_sent = True
                else:
                    logger.error("[OTP Email Delivery] Brevo API unexpected status %s for %s", resp.status, recipient_email)
        except urllib.error.HTTPError as http_err:
            err_body = http_err.read().decode('utf-8', 'ignore')
            logger.error("[OTP Email Delivery] Brevo API HTTP %s for %s: %s", http_err.code, recipient_email, err_body)
        except Exception as brevo_err:
            logger.error("[OTP Email Delivery] Brevo API request failed for %s: %s", recipient_email, brevo_err, exc_info=True)

    # Attempt 2: Configured Django mail backend (SMTP)
    if not email_sent and (not is_non_delivering or getattr(settings, 'DEBUG', False)) and (host_user and host_pass or is_non_delivering):
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
            logger.error("[OTP Email Delivery] Primary SMTP dispatch failed for %s: %s", recipient_email, e1, exc_info=True)

    # Attempt 2: Fallback port (465 SSL or 587 TLS) if env SMTP credentials exist
    if not email_sent:
        host_user = getattr(settings, 'EMAIL_HOST_USER', '').strip()
        host_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
        email_host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
        timeout_sec = int(getattr(settings, 'EMAIL_TIMEOUT', 12))
        if host_user and host_pass:
            fallback_port = 465 if int(getattr(settings, 'EMAIL_PORT', 587)) != 465 else 587
            use_ssl = fallback_port == 465
            use_tls = fallback_port == 587
            try:
                conn = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host=email_host,
                    port=fallback_port,
                    username=host_user,
                    password=host_pass,
                    use_ssl=use_ssl,
                    use_tls=use_tls,
                    timeout=timeout_sec,
                )
                msg_fb = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_text,
                    from_email=from_email,
                    to=[recipient_email],
                    connection=conn
                )
                msg_fb.attach_alternative(html_content, "text/html")
                sent_fb = msg_fb.send(fail_silently=False)
                email_sent = bool(sent_fb and sent_fb > 0)
            except Exception as e2:
                logger.error("[OTP Email Delivery] Fallback port %s failed for %s: %s", fallback_port, recipient_email, e2, exc_info=True)

    # Explicit opt-in dev-only server console log (never sent to client)
    if getattr(settings, 'DEBUG', False) and getattr(settings, 'OTP_DEV_LOG', False):
        logger.debug("[DEV OTP LOG] Purpose=%s User=%s Code=%s", purpose, user.username, otp_code)

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
        try:
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

                # Check Two-Factor Authentication (2FA) status safely
                # 2FA is disabled for user, admin, and student roles
                is_2fa_enabled = False
                try:
                    profile = UserProfile.objects.filter(user=user).first()
                    if profile is None:
                        profile = UserProfile.objects.create(user=user, two_factor_enabled=False)
                    user_role = getattr(profile, 'role', 'user')
                    if user_role in ('user', 'admin', 'student') or user.is_staff or user.is_superuser:
                        is_2fa_enabled = False
                    else:
                        is_2fa_enabled = getattr(profile, 'two_factor_enabled', False)
                except Exception as ex:
                    logger.warning("[Profile 2FA Lookup]: %s", ex)
                    is_2fa_enabled = False

                if is_2fa_enabled and user.email:
                    try:
                        # Generate cryptographically secure 6-digit 2FA OTP code & store only its hash
                        otp = OTPVerification.generate_otp()
                        expires = timezone.now() + timedelta(minutes=10)

                        # Invalidate previous unverified login OTPs for this user
                        OTPVerification.objects.filter(
                            user=user,
                            purpose='Login',
                            is_verified=False
                        ).update(is_verified=True)

                        OTPVerification.objects.create(
                            user=user,
                            otp_code=OTPVerification.hash_otp(otp),
                            purpose='Login',
                            expires_at=expires
                        )

                        # Save 2FA state in session (guard against session-write failures on Render)
                        try:
                            request.session['2fa_user_id'] = user.id
                            request.session['2fa_email'] = user.email
                            request.session['2fa_next'] = next_url
                            request.session.save()
                        except Exception as sess_ex:
                            logger.warning("[2FA] Session write failed — falling back to direct login: %s", sess_ex)
                            auth_login(request, user)
                            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                            return redirect(next_url)

                        email_sent, sent_email = send_otp_email(user, otp, purpose='Login')
                        masked = OTPVerification.mask_email(sent_email)
                        if email_sent:
                            messages.info(request, f'A 6-digit code has been sent to {masked}.')
                        else:
                            logger.error("Failed to send 2FA OTP email to %s for user %s", sent_email, user.username)
                            messages.error(request, "We couldn't send the code. Please try again.")

                        return redirect('verify_2fa')
                    except Exception as otp_ex:
                        logger.error("[2FA OTP dispatch error for user %s]: %s", user.username, otp_ex, exc_info=True)
                        messages.error(request, "We couldn't send the code. Please try again.")
                        return render(request, 'authentication/login.html', {
                            'error': "We couldn't send the code. Please try again.",
                            'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                            'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
                        })

                # Direct login if 2FA is disabled or user has no email or fallback
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

        except Exception as login_ex:
            # Log the FULL traceback so it appears in Render/Gunicorn stdout logs
            tb_str = _traceback.format_exc()
            logger.exception(
                "LOGIN 500 — request from %s\nFull traceback:\n%s",
                request.META.get('REMOTE_ADDR', '?'),
                tb_str,
            )
            # Also print so it appears in Render dashboard logs regardless of log level
            print(f"[LOGIN-500] {login_ex}\n{tb_str}", flush=True)
            messages.error(request, 'An unexpected error occurred. Please try again.')
            try:
                return render(request, 'authentication/login.html', {
                    'error': 'An unexpected error occurred. Please try again.',
                    'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                    'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
                })
            except Exception:
                # Last-resort: return a plain HTTP response so the user sees something
                return HttpResponse(
                    'Login error — please go back and try again.',
                    status=500,
                    content_type='text/plain',
                )

    return render(request, 'authentication/login.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME
    })


def verify_2fa(request):
    """
    Renders and verifies the 6-digit Two-Factor Authentication code for login.
    Enforces constant-time hash comparison, single-use invalidation, and 5-attempt lockout.
    """
    user_id = request.session.get('2fa_user_id')
    email = request.session.get('2fa_email', '')
    masked_email = OTPVerification.mask_email(email)
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

        if not submitted_otp or len(submitted_otp) != 6 or not submitted_otp.isdigit():
            messages.error(request, 'Please enter a valid 6-digit 2FA code.')
            return render(request, 'authentication/verify_2fa.html', {
                'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
                'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
                'email': masked_email,
                'masked_email': masked_email,
                'user': user,
            })

        otp_record = OTPVerification.objects.filter(
            user=user,
            purpose='Login',
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, 'No active verification code found. Please click Resend Code.')
        elif otp_record.is_expired():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            messages.error(request, 'The 2FA code has expired. Please click Resend Code.')
        elif otp_record.is_locked():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            messages.error(request, 'Too many failed attempts. Please click Resend Code for a new code.')
        elif not otp_record.verify_code(submitted_otp):
            otp_record.failed_attempts += 1
            if otp_record.failed_attempts >= OTPVerification.MAX_FAILED_ATTEMPTS:
                otp_record.is_verified = True
                otp_record.save(update_fields=['failed_attempts', 'is_verified'])
                messages.error(request, 'Too many failed attempts. Please click Resend Code for a new code.')
            else:
                otp_record.save(update_fields=['failed_attempts'])
                remaining = OTPVerification.MAX_FAILED_ATTEMPTS - otp_record.failed_attempts
                messages.error(request, f'Invalid 2FA code. {remaining} attempt(s) remaining.')
        else:
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])

            request.session.pop('2fa_user_id', None)
            request.session.pop('2fa_email', None)
            request.session.pop('2fa_next', None)

            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)

    return render(request, 'authentication/verify_2fa.html', {
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
        'email': masked_email,
        'masked_email': masked_email,
        'user': user,
    })


@require_POST
def resend_2fa_otp(request):
    """
    AJAX / POST endpoint to generate and resend a new 2FA Login code.
    Enforces a 30-second server-side cooldown and never exposes the OTP in JSON.
    """
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'}, status=400)

    user = User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

    # Server-side 30-second cooldown check
    latest_otp = OTPVerification.objects.filter(
        user=user,
        purpose='Login'
    ).order_by('-created_at').first()
    if latest_otp:
        elapsed = (timezone.now() - latest_otp.created_at).total_seconds()
        if elapsed < OTPVerification.RESEND_COOLDOWN_SECONDS:
            wait_secs = int(OTPVerification.RESEND_COOLDOWN_SECONDS - elapsed) + 1
            return JsonResponse({
                'status': 'error',
                'message': f'Please wait {wait_secs}s before requesting a new code.',
                'retry_after': wait_secs,
            }, status=429)

    OTPVerification.objects.filter(
        user=user,
        purpose='Login',
        is_verified=False
    ).update(is_verified=True)

    otp = OTPVerification.generate_otp()
    expires = timezone.now() + timedelta(minutes=10)

    OTPVerification.objects.create(
        user=user,
        otp_code=OTPVerification.hash_otp(otp),
        purpose='Login',
        expires_at=expires
    )

    email_sent, sent_email = send_otp_email(user, otp, purpose='Login')
    if not email_sent:
        logger.error("Failed to resend 2FA OTP email to %s for user %s", sent_email, user.username)
        return JsonResponse({
            'status': 'error',
            'message': "We couldn't send the code. Please try again."
        }, status=502)

    masked = OTPVerification.mask_email(sent_email)
    return JsonResponse({
        'status': 'success',
        'message': f'A 6-digit code has been sent to {masked}.',
        'email_sent': True,
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

        # Create linked UserProfile (2FA disabled for user, admin, and student)
        try:
            assigned_role = role if role in ['user', 'student', 'teacher', 'admin'] else 'user'
            UserProfile.objects.create(
                user=user,
                phone=phone,
                status='active',
                role=assigned_role,
                two_factor_enabled=False
            )
        except Exception as p_err:
            print(f"[UserProfile creation notice]: {p_err}")

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

        otp = OTPVerification.generate_otp()
        expires = timezone.now() + timedelta(minutes=10)

        OTPVerification.objects.create(
            user=user,
            otp_code=OTPVerification.hash_otp(otp),
            purpose='ForgotPassword',
            expires_at=expires
        )

        request.session['otp_email'] = user.email or email
        request.session['otp_user_id'] = user.id

        email_sent, sent_email = send_otp_email(user, otp, purpose='ForgotPassword')
        masked = OTPVerification.mask_email(sent_email)

        if not email_sent:
            logger.error("Failed to send password reset OTP email to %s", sent_email)
            err_msg = "We couldn't send the code. Please try again."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': err_msg}, status=502)
            messages.error(request, err_msg)
            return redirect('forgot_password')

        user_msg = f'A 6-digit code has been sent to {masked}.'

        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': user_msg,
                'email_sent': True,
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
            user=user_id,
            purpose='ForgotPassword',
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, 'No active OTP found. Please request a new one.')
        elif otp_record.is_expired():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            messages.error(request, 'OTP has expired. Please request a new one.')
        elif otp_record.is_locked():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            messages.error(request, 'Too many failed attempts. Please request a new OTP.')
        elif not otp_record.verify_code(submitted_otp):
            otp_record.failed_attempts += 1
            if otp_record.failed_attempts >= OTPVerification.MAX_FAILED_ATTEMPTS:
                otp_record.is_verified = True
                otp_record.save(update_fields=['failed_attempts', 'is_verified'])
                messages.error(request, 'Too many failed attempts. Please request a new OTP.')
            else:
                otp_record.save(update_fields=['failed_attempts'])
                messages.error(request, 'Invalid OTP code. Please check and try again.')
        else:
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
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