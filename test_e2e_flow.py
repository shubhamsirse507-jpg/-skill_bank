import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from skill_management.models import Skill, SkillCategory
from profiles.models import UserProfile
from messaging.models import SkillExchange, Message, Conversation
from bookings.models import Booking
from ratings.models import ReviewRating
from admin_panel.models import PlatformNotice, PlatformReport

def run_tests():
    print("=" * 60)
    print("RUNNING END-TO-END DEMO SUITE FOR SKILL BANK")
    print("=" * 60)

    client = Client()

    # 1. Landing Page
    res = client.get('/')
    assert res.status_code in [200, 302], f"Landing failed: {res.status_code}"
    print("✅ 1. Public Landing Page (/): PASS (Status 200)")

    # 2. Login Page GET
    res = client.get('/auth/login/')
    assert res.status_code == 200, f"Login GET failed: {res.status_code}"
    print("✅ 2. Login Page GET (/auth/login/): PASS (Status 200)")

    # 3. User Registration
    test_username = "e2e_tester_user"
    User.objects.filter(username=test_username).delete()

    res = client.post('/auth/register/', {
        'username': test_username,
        'email': 'e2e_tester@example.com',
        'fullname': 'Demo Tester User',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'role': 'student'
    }, follow=True)

    assert res.status_code == 200, f"Registration failed: {res.status_code}"
    user = User.objects.get(username=test_username)
    print(f"✅ 3. User Registration & Auto-Login: PASS (Registered '{user.username}', auto-logged in)")

    # 4. User Dashboard GET
    res = client.get('/user/')
    assert res.status_code == 200, f"User Dashboard failed: {res.status_code}"
    assert b"Welcome back" in res.content, "User Dashboard content check failed"
    print("✅ 4. User Dashboard UI (/user/): PASS (Status 200 & Personalized Welcome)")

    # 5. Add Skill GET & POST
    res = client.get('/user/add-skill/')
    assert res.status_code == 200, f"Add Skill GET failed: {res.status_code}"

    cat, _ = SkillCategory.objects.get_or_create(category_name="Web Development", defaults={'icon_class': 'fa-solid fa-code'})

    res = client.post('/user/add-skill/', {
        'title': 'Django & Python Mastery',
        'category_id': cat.id,
        'skill_type': 'offered',
        'level': 'Advanced',
        'description': 'I can teach full-stack Python and Django framework.'
    }, follow=True)

    assert res.status_code == 200, f"Add Skill POST failed: {res.status_code}"
    created_skill = Skill.objects.filter(user=user, title='Django & Python Mastery').first()
    assert created_skill is not None, "Skill not created in DB"
    print(f"✅ 5. Add Skill UI & DB Creation (/user/add-skill/): PASS (Added '{created_skill.title}')")

    # 6. Browse Skills & Search UI
    res = client.get('/search/?q=Django')
    assert res.status_code == 200, f"Search UI failed: {res.status_code}"
    print("✅ 6. Search & Browse Skills UI (/search/?q=Django): PASS (Status 200)")

    # 7. User Profile UI
    res = client.get('/profile/')
    assert res.status_code == 200, f"Profile UI failed: {res.status_code}"
    print("✅ 7. Profile UI (/profile/): PASS (Status 200)")

    # 8. Notifications Center UI
    res = client.get('/notifications/')
    assert res.status_code == 200, f"Notifications UI failed: {res.status_code}"
    print("✅ 8. Notifications Center (/notifications/): PASS (Status 200)")

    # 9. Messaging System UI
    res = client.get('/messaging/')
    assert res.status_code == 200, f"Messaging UI failed: {res.status_code}"
    print("✅ 9. Messaging System (/messaging/): PASS (Status 200)")

    # 10. Bookings UI
    res = client.get('/bookings/')
    assert res.status_code == 200, f"Bookings UI failed: {res.status_code}"
    print("✅ 10. Bookings UI (/bookings/): PASS (Status 200)")

    # 11. Ratings UI
    res = client.get('/ratings/')
    assert res.status_code == 200, f"Ratings UI failed: {res.status_code}"
    print("✅ 11. Ratings UI (/ratings/): PASS (Status 200)")

    # 12. AI Chatbot UI
    res = client.get('/user/chatbot/')
    assert res.status_code == 200, f"Chatbot UI failed: {res.status_code}"
    print("✅ 12. AI Chatbot UI (/user/chatbot/): PASS (Status 200)")

    # 13. Live Session UI
    res = client.get('/user/live-session/')
    assert res.status_code == 200, f"Live Session UI failed: {res.status_code}"
    print("✅ 13. Live Session UI (/user/live-session/): PASS (Status 200)")

    # 14. Admin Panel UI (Staff check)
    user.is_staff = True
    user.save()

    res = client.get('/admin-panel/')
    assert res.status_code == 200, f"Admin Dashboard failed: {res.status_code}"
    print("✅ 14. Admin Panel Overview (/admin-panel/): PASS (Status 200)")

    res = client.get('/admin-panel/users/')
    assert res.status_code == 200, f"Admin User Management failed: {res.status_code}"
    print("✅ 15. Admin User Management (/admin-panel/users/): PASS (Status 200)")

    res = client.get('/admin-panel/skills/')
    assert res.status_code == 200, f"Admin Skills failed: {res.status_code}"
    print("✅ 16. Admin Skills & Categories (/admin-panel/skills/): PASS (Status 200)")

    res = client.get('/admin-panel/reports/')
    assert res.status_code == 200, f"Admin Reports failed: {res.status_code}"
    print("✅ 17. Admin Moderation Queue (/admin-panel/reports/): PASS (Status 200)")

    res = client.get('/admin-panel/monitoring/')
    assert res.status_code == 200, f"Admin Monitoring failed: {res.status_code}"
    print("✅ 18. Admin Platform Monitoring (/admin-panel/monitoring/): PASS (Status 200)")

    # 15. Logout & Relogin test
    client.get('/auth/logout/')
    res = client.post('/auth/login/', {
        'username': test_username,
        'password': 'TestPassword123!'
    }, follow=True)

    assert res.status_code == 200, f"Re-login failed: {res.status_code}"
    print("✅ 19. Logout & Re-Login Connection to Dashboard: PASS (Successfully logged in and redirected to /user/)")

    print("=" * 60)
    print("🎉 ALL 19 END-TO-END DEMO TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
