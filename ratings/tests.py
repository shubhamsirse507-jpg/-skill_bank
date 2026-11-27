from datetime import date, time
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from bookings.models import Booking
from bookings.views import booking_list, complete_booking
from messaging.models import SkillExchange
from skill_management.models import Skill, SkillCategory
from .models import ReviewRating
from .views import rating_view


def _attach_session_and_messages(request, user):
    """Attach session, messages, and authenticated user to a RequestFactory request."""
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)
    request.user = user
    return request


class RatingFeatureTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.requester = User.objects.create_user(username='learner1', password='Password123!')
        self.provider = User.objects.create_user(username='mentor1', password='Password123!')
        self.outsider = User.objects.create_user(username='outsider1', password='Password123!')

        self.category = SkillCategory.objects.create(category_name='Programming')
        self.skill = Skill.objects.create(
            user=self.provider,
            category=self.category,
            title='Django Mastery',
            skill_type='offered',
            status='approved',
        )
        self.exchange = SkillExchange.objects.create(
            requester=self.requester,
            receiver=self.provider,
            skill=self.skill,
            title='Django 1-on-1 Session',
            status='accepted',
        )
        self.booking = Booking.objects.create(
            request=self.exchange,
            scheduled_date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status='scheduled',
        )

    def test_ratings_page_renders_form_even_without_bookings(self):
        req = _attach_session_and_messages(
            self.factory.get(reverse('ratings:rating_dashboard')),
            self.outsider,
        )
        res = rating_view(req)
        self.assertEqual(res.status_code, 200)
        html = res.content.decode()
        self.assertIn('Leave a Review', html)
        self.assertIn('name="communication_rating"', html)
        self.assertIn('name="clarity_rating"', html)
        self.assertIn('name="punctuality_rating"', html)
        self.assertIn('name="would_recommend"', html)
        self.assertIn('0% Recommendation Rate', html)
        self.assertIn('star-empty', html)

    def test_complete_booking_and_submit_web_review(self):
        # Booking list renders Mark Completed for scheduled sessions
        list_req = _attach_session_and_messages(
            self.factory.get(reverse('booking_list')),
            self.requester,
        )
        list_res = booking_list(list_req)
        self.assertEqual(list_res.status_code, 200)
        self.assertIn('Mark Completed', list_res.content.decode())

        # Non-participant cannot complete booking
        bad_complete = _attach_session_and_messages(
            self.factory.post(reverse('complete_booking', args=[self.booking.id])),
            self.outsider,
        )
        res = complete_booking(bad_complete, self.booking.id)
        self.assertEqual(res.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'scheduled')

        # Participant marks booking completed
        good_complete = _attach_session_and_messages(
            self.factory.post(reverse('complete_booking', args=[self.booking.id])),
            self.requester,
        )
        res = complete_booking(good_complete, self.booking.id)
        self.assertEqual(res.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'completed')

        # Submit review via web UI
        post_req = _attach_session_and_messages(
            self.factory.post(reverse('ratings:rating_dashboard'), {
                'booking_id': self.booking.id,
                'rating': 5,
                'communication_rating': 4,
                'clarity_rating': 5,
                'punctuality_rating': 4,
                'tags': 'Patient, Clear Explanations',
                'comment': 'Very helpful session!',
                'would_recommend': 'on',
            }),
            self.requester,
        )
        res = rating_view(post_req)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('ratings:rating_dashboard'))
        self.assertEqual(ReviewRating.objects.count(), 1)
        review = ReviewRating.objects.first()
        self.assertEqual(review.reviewer, self.requester)
        self.assertEqual(review.reviewed_user, self.provider)
        self.assertEqual(review.communication_rating, 4)
        self.assertTrue(review.would_recommend)

        # Duplicate review by same user is blocked
        dup_req = _attach_session_and_messages(
            self.factory.post(reverse('ratings:rating_dashboard'), {
                'booking_id': self.booking.id,
                'rating': 3,
                'comment': 'Duplicate attempt',
            }),
            self.requester,
        )
        res = rating_view(dup_req)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(ReviewRating.objects.count(), 1)

        # Other participant can still review the same booking
        get_prov = _attach_session_and_messages(
            self.factory.get(reverse('ratings:rating_dashboard')),
            self.provider,
        )
        self.assertIn(self.exchange.title, rating_view(get_prov).content.decode())

        post_prov = _attach_session_and_messages(
            self.factory.post(reverse('ratings:rating_dashboard'), {
                'booking_id': self.booking.id,
                'rating': 5,
                'communication_rating': 5,
                'clarity_rating': 5,
                'punctuality_rating': 5,
                'comment': 'Great student!',
                'would_recommend': 'on',
            }),
            self.provider,
        )
        res = rating_view(post_prov)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(ReviewRating.objects.count(), 2)

        # Tabs filter properly
        tab_req = _attach_session_and_messages(
            self.factory.get(reverse('ratings:rating_dashboard'), {'tab': 'received'}),
            self.provider,
        )
        tab_html = rating_view(tab_req).content.decode()
        self.assertIn('Very helpful session!', tab_html)
        self.assertNotIn('Great student!', tab_html)

    def test_ratings_api_validation_and_permissions(self):
        api = APIClient()

        # Outsider cannot create review via /api/v1/ratings/
        api.force_authenticate(user=self.outsider)
        res = api.post('/api/v1/ratings/', {
            'booking': self.booking.id,
            'rating': 5,
            'comment': 'Unauthorized',
        })
        self.assertEqual(res.status_code, 403)

        # Invalid score rejected
        api.force_authenticate(user=self.requester)
        res = api.post('/api/v1/ratings/', {
            'booking': self.booking.id,
            'rating': 6,
            'communication_rating': 0,
            'comment': 'Bad score',
        })
        self.assertEqual(res.status_code, 400)

        # Valid create via /ratings/api/ derives reviewed_user and ignores spoofed reviewed_user
        res = api.post('/ratings/api/', {
            'booking': self.booking.id,
            'reviewed_user': self.outsider.id,
            'rating': 4,
            'communication_rating': 4,
            'clarity_rating': 5,
            'punctuality_rating': 4,
            'comment': 'Solid API session',
            'would_recommend': True,
        })
        self.assertEqual(res.status_code, 201)
        review = ReviewRating.objects.get(id=res.data['id'])
        self.assertEqual(review.reviewed_user, self.provider)

        # Non-author cannot edit or delete via /api/v1/ratings/<id>/
        api.force_authenticate(user=self.provider)
        res = api.patch(f'/api/v1/ratings/{review.id}/', {'comment': 'Tampered'})
        self.assertEqual(res.status_code, 403)
        res = api.delete(f'/api/v1/ratings/{review.id}/')
        self.assertEqual(res.status_code, 403)

        # Author can update own review
        api.force_authenticate(user=self.requester)
        res = api.patch(f'/api/v1/ratings/{review.id}/', {'comment': 'Updated feedback'})
        self.assertEqual(res.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.comment, 'Updated feedback')
