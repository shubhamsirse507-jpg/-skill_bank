"""
test_auth_and_2fa.py
Comprehensive test suite verifying Authentication, Two-Factor Authentication (2FA),
OTP verification, password reset, and REST API endpoints.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.utils import timezone
from datetime import timedelta
import json

from profiles.models import UserProfile
from authentication.models import OTPVerification
from authentication import views as auth_views
from fix_missing_tables import fix_schema

def run_tests():
    print("\n" + "="*70)
    print("🚀 RUNNING Skill-Verse AUTH & 2FA VERIFICATION SUITE")
    print("="*70)

    # Step 0: Ensure DB schema & column integrity
    print("\n[STEP 0] Ensuring Database Schema Integrity...")
    fix_schema()
    print("✅ Schema verified.")

    rf = RequestFactory()

    # Helper to add session & messages to mock request
    def prepare_request(req):
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(req)
        req.session.save()
        msg_middleware = MessageMiddleware(lambda r: None)
        msg_middleware.process_request(req)
        return req

    # Clean up test users if existing
    User.objects.filter(username__in=['test_2fa_user', 'test_no_2fa_user', 'new_reg_user']).delete()

    # Step 1: Test Registration
    print("\n[STEP 1] Testing User Registration...")
    reg_req = rf.post('/register/', {
        'username': 'test_2fa_user',
        'email': 'test2fa@Skill-Verse.com',
        'first_name': 'Test',
        'last_name': 'TwoFactor',
        'password': 'SecurePassword@123',
        'confirm_password': 'SecurePassword@123',
        'role': 'student',
        'phone': '1234567890'
    })
    prepare_request(reg_req)
    reg_res = auth_views.register(reg_req)
    assert reg_res.status_code == 302, f"Expected 302 redirect on register, got {reg_res.status_code}"
    
    test_user = User.objects.filter(username='test_2fa_user').first()
    assert test_user is not None, "Test user was not created in DB!"
    assert test_user.profile is not None, "UserProfile was not created!"
    assert test_user.profile.two_factor_enabled is True, "2FA was not enabled by default!"
    print(f"✅ User registered successfully: {test_user.username} (Role: {test_user.profile.role}, 2FA: {test_user.profile.two_factor_enabled})")

    # Step 2: Test Login with 2FA
    print("\n[STEP 2] Testing Login with 2FA Enabled...")
    login_req = rf.post('/login/', {
        'username': 'test_2fa_user',
        'password': 'SecurePassword@123'
    })
    prepare_request(login_req)
    login_res = auth_views.login(login_req)
    assert login_res.status_code == 302, f"Expected 302 redirect, got {login_res.status_code}"
    assert login_res.url == '/verify-2fa/', f"Expected redirect to /verify-2fa/, got {login_res.url}"
    assert login_req.session.get('2fa_user_id') == test_user.id, "Session missing 2fa_user_id!"

    # Check that OTP was created in database
    otp_record = OTPVerification.objects.filter(user=test_user, purpose='Login', is_verified=False).order_by('-created_at').first()
    assert otp_record is not None, "Login OTP record was not created!"
    assert len(otp_record.otp_code) == 6, f"Invalid OTP code length: {otp_record.otp_code}"
    print(f"✅ Login 2FA OTP generated successfully: {otp_record.otp_code} for {test_user.email}")

    # Step 3: Test 2FA Verification with Wrong Code
    print("\n[STEP 3] Testing 2FA Verification with Invalid Code...")
    verify_req_bad = rf.post('/verify-2fa/', {'otp': '000000'})
    prepare_request(verify_req_bad)
    verify_req_bad.session['2fa_user_id'] = test_user.id
    verify_req_bad.session['2fa_email'] = test_user.email
    verify_res_bad = auth_views.verify_2fa(verify_req_bad)
    assert verify_res_bad.status_code == 200, "Should re-render page on invalid OTP"
    assert not OTPVerification.objects.get(id=otp_record.id).is_verified, "OTP should NOT be verified"
    print("✅ Invalid 2FA OTP correctly rejected.")

    # Step 4: Test 2FA Verification with Valid Code
    print("\n[STEP 4] Testing 2FA Verification with Valid Code...")
    verify_req_good = rf.post('/verify-2fa/', {
        'd1': otp_record.otp_code[0],
        'd2': otp_record.otp_code[1],
        'd3': otp_record.otp_code[2],
        'd4': otp_record.otp_code[3],
        'd5': otp_record.otp_code[4],
        'd6': otp_record.otp_code[5],
    })
    prepare_request(verify_req_good)
    verify_req_good.session['2fa_user_id'] = test_user.id
    verify_req_good.session['2fa_email'] = test_user.email
    verify_res_good = auth_views.verify_2fa(verify_req_good)
    assert verify_res_good.status_code == 302, f"Expected 302 redirect upon successful 2FA, got {verify_res_good.status_code}"
    assert OTPVerification.objects.get(id=otp_record.id).is_verified is True, "OTP record should be verified"
    print("✅ 2FA code successfully verified and session authenticated!")

    # Step 5: Test Resend 2FA Code AJAX
    print("\n[STEP 5] Testing Resend 2FA Code (AJAX)...")
    resend_req = rf.post('/resend-2fa/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    prepare_request(resend_req)
    resend_req.session['2fa_user_id'] = test_user.id
    resend_res = auth_views.resend_2fa_otp(resend_req)
    assert resend_res.status_code == 200, f"Expected 200 JSON, got {resend_res.status_code}"
    resend_data = json.loads(resend_res.content)
    assert resend_data.get('status') == 'success', f"Expected success status, got {resend_data}"
    new_otp = OTPVerification.objects.filter(user=test_user, purpose='Login', is_verified=False).order_by('-created_at').first()
    assert new_otp is not None, "New OTP was not created on resend!"
    print(f"✅ Resend 2FA returned success: {resend_data['message']} (New Code: {new_otp.otp_code})")

    # Step 6: Test Login with 2FA Disabled
    print("\n[STEP 6] Testing Login with 2FA Disabled...")
    test_user.profile.two_factor_enabled = False
    test_user.profile.save()

    login_req2 = rf.post('/login/', {
        'username': 'test_2fa_user',
        'password': 'SecurePassword@123'
    })
    prepare_request(login_req2)
    login_res2 = auth_views.login(login_req2)
    assert login_res2.status_code == 302, "Expected redirect"
    assert login_res2.url == '/user/' or login_res2.url == 'home', f"Expected home dashboard redirect, got {login_res2.url}"
    print("✅ Login with 2FA disabled logged in directly without 2FA prompt.")

    # Re-enable 2FA
    test_user.profile.two_factor_enabled = True
    test_user.profile.save()

    # Step 7: Test Forgot Password OTP & Password Reset Flow
    print("\n[STEP 7] Testing Forgot Password OTP & Reset...")
    forgot_req = rf.post('/forgot-password/', {'email': 'test2fa@Skill-Verse.com'})
    prepare_request(forgot_req)
    forgot_res = auth_views.forgot_password(forgot_req)
    assert forgot_res.status_code == 302, "Expected redirect to verify_otp"
    assert forgot_res.url == '/verify-otp/', f"Expected redirect to /verify-otp/, got {forgot_res.url}"

    reset_otp_rec = OTPVerification.objects.filter(user=test_user, purpose='ForgotPassword', is_verified=False).order_by('-created_at').first()
    assert reset_otp_rec is not None, "Forgot password OTP record missing!"
    print(f"✅ Forgot password OTP created: {reset_otp_rec.otp_code}")

    # Verify Reset OTP
    verify_reset_req = rf.post('/verify-otp/', {'otp': reset_otp_rec.otp_code})
    prepare_request(verify_reset_req)
    verify_reset_req.session['otp_user_id'] = test_user.id
    verify_reset_req.session['otp_email'] = test_user.email
    verify_reset_res = auth_views.verify_otp(verify_reset_req)
    assert verify_reset_res.status_code == 302, "Expected redirect to reset_password"
    assert verify_reset_res.url == '/reset-password/', f"Expected /reset-password/, got {verify_reset_res.url}"
    assert verify_reset_req.session.get('otp_verified_user_id') == test_user.id
    print("✅ Password Reset OTP verified successfully.")

    # Perform Password Reset
    reset_req = rf.post('/reset-password/', {
        'password': 'BrandNewPassword@456',
        'confirm_password': 'BrandNewPassword@456'
    })
    prepare_request(reset_req)
    reset_req.session['otp_verified_user_id'] = test_user.id
    reset_res = auth_views.reset_password(reset_req)
    assert reset_res.status_code == 302, "Expected redirect to login"
    assert reset_res.url == '/login/', f"Expected /login/, got {reset_res.url}"

    # Verify new password works
    updated_user = User.objects.get(id=test_user.id)
    assert updated_user.check_password('BrandNewPassword@456'), "Password was not updated in DB!"
    print("✅ Password reset successfully and verified with check_password!")

    # Step 8: Test Safe Handling of Non-Existent Email (No Data Corruption)
    print("\n[STEP 8] Testing Non-Existent Email Safe Handling...")
    non_existent_req = rf.post('/forgot-password/', {'email': 'does_not_exist_9999@random.com'})
    prepare_request(non_existent_req)
    non_existent_res = auth_views.forgot_password(non_existent_req)
    # Ensure no demo user's email was mutated
    assert User.objects.filter(email='does_not_exist_9999@random.com').count() == 0, "Non-existent user was created or hijacked!"
    print("✅ Non-existent email handled safely without modifying existing database users.")

    # Step 9: Test REST API Endpoints
    print("\n[STEP 9] Testing REST API 2FA & Auth Endpoints...")
    client = Client()
    
    # REST API Login with 2FA
    api_login_res = client.post('/api/v1/auth/login/', json.dumps({
        'username': 'test_2fa_user',
        'password': 'BrandNewPassword@456'
    }), content_type='application/json')
    assert api_login_res.status_code == 200, f"API Login failed: {api_login_res.content}"
    api_login_data = api_login_res.json()
    assert api_login_data.get('data', {}).get('two_factor_required') is True, f"Expected 2FA required, got {api_login_data}"
    api_otp = OTPVerification.objects.filter(user=test_user, purpose='Login', is_verified=False).order_by('-created_at').first().otp_code
    print(f"✅ REST API Login requires 2FA: {api_login_data['data']['message']}")

    # REST API Verify 2FA
    api_verify_res = client.post('/api/v1/auth/verify-2fa/', json.dumps({
        'user_id': test_user.id,
        'otp': api_otp
    }), content_type='application/json')
    assert api_verify_res.status_code == 200, f"API Verify 2FA failed: {api_verify_res.content}"
    api_verify_data = api_verify_res.json()
    assert 'tokens' in api_verify_data.get('data', {}), "JWT tokens missing in API response!"
    print(f"✅ REST API 2FA Verified! Received JWT Access Token: {api_verify_data['data']['tokens']['access'][:20]}...")

    # Cleanup
    User.objects.filter(username='test_2fa_user').delete()

    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED! AUTHENTICATION & 2FA OTP WORKING PERFECTLY!")
    print("="*70 + "\n")

if __name__ == '__main__':
    run_tests()
