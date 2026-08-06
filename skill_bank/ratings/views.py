from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg
from messaging.models import SkillExchange
from .models import ReviewRating


def get_demo_user(request):
    if request.user.is_authenticated:
        return request.user
    user = User.objects.filter(username='dnyani').first() or User.objects.first()
    return user


def rating_view(request):
    current_user = get_demo_user(request)
    reviews = ReviewRating.objects.select_related('reviewer', 'reviewee', 'exchange').all()

    # Calculate Summary Stats
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
    avg_rating = round(avg_rating, 1)

    avg_comm = reviews.aggregate(Avg('communication_rating'))['communication_rating__avg'] or 0.0
    avg_comm = round(avg_comm, 1)

    avg_clarity = reviews.aggregate(Avg('clarity_rating'))['clarity_rating__avg'] or 0.0
    avg_clarity = round(avg_clarity, 1)

    avg_punc = reviews.aggregate(Avg('punctuality_rating'))['punctuality_rating__avg'] or 0.0
    avg_punc = round(avg_punc, 1)

    rec_count = reviews.filter(would_recommend=True).count()
    recommend_pct = int((rec_count / total_reviews * 100)) if total_reviews > 0 else 100

    # Rating distribution breakdown (5 stars to 1 star)
    star_counts = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }
    star_percents = {}
    for star, count in star_counts.items():
        star_percents[star] = int((count / total_reviews * 100)) if total_reviews > 0 else 0

    # Exchanges ready to review
    unreviewed_exchanges = SkillExchange.objects.filter(reviews__isnull=True)

    # Handle submitting new rating form
    if request.method == 'POST':
        exchange_id = request.POST.get('exchange_id')
        exchange = get_object_or_404(SkillExchange, id=exchange_id)
        
        rating = int(request.POST.get('rating', 5))
        comm_rating = int(request.POST.get('communication_rating', 5))
        clarity_rating = int(request.POST.get('clarity_rating', 5))
        punc_rating = int(request.POST.get('punctuality_rating', 5))
        comment = request.POST.get('comment', '').strip()
        tags = request.POST.get('tags', '')
        would_recommend = request.POST.get('would_recommend') == 'on'

        reviewer = current_user if current_user else exchange.requester
        reviewee = exchange.provider if reviewer == exchange.requester else exchange.requester

        ReviewRating.objects.create(
            exchange=exchange,
            reviewer=reviewer,
            reviewee=reviewee,
            rating=rating,
            communication_rating=comm_rating,
            clarity_rating=clarity_rating,
            punctuality_rating=punc_rating,
            comment=comment,
            tags=tags,
            would_recommend=would_recommend
        )

        exchange.status = 'COMPLETED'
        exchange.save()

        messages.success(request, "Thank you! Your rating and feedback have been published.")
        return redirect('rating_dashboard')

    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'avg_comm': avg_comm,
        'avg_clarity': avg_clarity,
        'avg_punc': avg_punc,
        'recommend_pct': recommend_pct,
        'star_counts': star_counts,
        'star_percents': star_percents,
        'unreviewed_exchanges': unreviewed_exchanges,
        'current_user': current_user,
    }
    return render(request, 'ratings/rating.html', context)
