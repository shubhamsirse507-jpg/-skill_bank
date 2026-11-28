from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from .models import Booking
from messaging.models import SkillExchange


@login_required
def booking_list(request):
    """Lists bookings for current user (as requester or receiver)."""
    bookings = []
    error_msg = None

    try:
        user_exchanges = list(SkillExchange.objects.filter(
            Q(requester=request.user) | Q(receiver=request.user)
        ))
        # Use list() to force QuerySet evaluation HERE (inside try/except),
        # not lazily in the template where we can't catch OperationalError.
        bookings = list(
            Booking.objects.filter(request__in=user_exchanges).select_related(
                'request', 'request__requester', 'request__receiver', 'request__skill'
            )
        )
        from ratings.models import ReviewRating
        reviewed_booking_ids = set(
            ReviewRating.objects.filter(
                reviewer=request.user, booking__in=bookings
            ).values_list('booking_id', flat=True)
        )
    except Exception as e:
        error_msg = str(e)
        bookings = []
        reviewed_booking_ids = set()

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
        'reviewed_booking_ids': reviewed_booking_ids,
        'error_msg': error_msg,
    })


@login_required
def complete_booking(request, booking_id):
    """Marks a scheduled booking as completed by one of its participants."""
    if request.method != 'POST':
        return redirect('booking_list')

    booking = get_object_or_404(
        Booking.objects.select_related('request', 'request__requester', 'request__receiver'),
        id=booking_id,
    )
    if request.user not in (booking.request.requester, booking.request.receiver):
        messages.error(request, 'You are not authorized to update this booking.')
        return redirect('booking_list')

    if booking.status == 'cancelled':
        messages.error(request, 'Cancelled bookings cannot be marked completed.')
        return redirect('booking_list')

    if booking.status != 'completed':
        booking.status = 'completed'
        booking.save(update_fields=['status'])
        messages.success(request, 'Session marked as completed! You can now leave a review.')
    return redirect('booking_list')


@login_required
def create_booking(request, exchange_id):
    """Schedules a new booking for an accepted exchange."""
    exchange = get_object_or_404(
        SkillExchange.objects.filter(Q(requester=request.user) | Q(receiver=request.user)),
        id=exchange_id
    )

    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meeting_mode = request.POST.get('meeting_mode', 'online')
        meeting_link = request.POST.get('meeting_link', '').strip()

        if not scheduled_date or not start_time or not end_time:
            messages.error(request, 'Please provide date, start time, and end time.')
            return redirect('create_booking', exchange_id=exchange_id)

        booking = Booking.objects.create(
            request=exchange,
            scheduled_date=scheduled_date,
            start_time=start_time,
            end_time=end_time,
            meeting_mode=meeting_mode,
            meeting_link=meeting_link,
            status='scheduled'
        )

        messages.success(request, 'Session booked successfully!')
        return redirect('booking_list')

    return render(request, 'bookings/create_booking.html', {
        'exchange': exchange,
    })


from .models import Batch, BatchEnrollment, DoubtCall
from skill_management.models import SkillCategory
from django.utils import timezone


def seed_rich_batches():
    """Seeds a rich collection of diverse live batches into the database."""
    from django.contrib.auth.models import User
    import datetime

    # Get or create instructors
    teacher = User.objects.filter(username='teacher_demo').first() or User.objects.filter(is_staff=True).first() or User.objects.first()
    student_instr = User.objects.filter(username='student_user').first() or teacher
    admin_instr = User.objects.filter(username='admin_demo').first() or teacher

    if not teacher:
        return

    # Categories
    cat_prog, _ = SkillCategory.objects.get_or_create(category_name="Programming", defaults={"description": "Coding & Web Dev", "icon_class": "fa-solid fa-code"})
    cat_design, _ = SkillCategory.objects.get_or_create(category_name="Design", defaults={"description": "UI/UX & Graphics", "icon_class": "fa-solid fa-pen-nib"})
    cat_music, _ = SkillCategory.objects.get_or_create(category_name="Music", defaults={"description": "Instruments & Vocals", "icon_class": "fa-solid fa-music"})
    cat_lang, _ = SkillCategory.objects.get_or_create(category_name="Language", defaults={"description": "Spoken & Written English", "icon_class": "fa-solid fa-language"})
    cat_data, _ = SkillCategory.objects.get_or_create(category_name="Data Science & AI", defaults={"description": "AI, ML & Analytics", "icon_class": "fa-solid fa-brain"})

    now = timezone.now()

    new_batches_data = [
        {
            "title": "Python & AI Prompt Engineering Masterclass",
            "instructor": teacher,
            "category": cat_data,
            "description": "Learn to build LLM-powered web apps, LangChain agents, OpenAI API integrations, and RAG pipelines.",
            "scheduled_at": now + datetime.timedelta(days=1, hours=5),
            "duration_minutes": 120,
            "max_seats": 20,
            "enrolled_count": 4,
            "price_credits": 120.00,
        },
        {
            "title": "Mastering Django REST Framework & WebSockets",
            "instructor": teacher,
            "category": cat_prog,
            "description": "A 2-hour intensive group class building real-time APIs, JWT authentication, and live chat rooms.",
            "scheduled_at": now + datetime.timedelta(days=2, hours=4),
            "duration_minutes": 120,
            "max_seats": 12,
            "enrolled_count": 3,
            "price_credits": 150.00,
        },
        {
            "title": "React 18 & Tailwind CSS UI Components Workshop",
            "instructor": teacher,
            "category": cat_prog,
            "description": "Build modern responsive dashboard UI components with React 18, Hooks, Framer Motion, and Tailwind CSS.",
            "scheduled_at": now + datetime.timedelta(days=3, hours=2),
            "duration_minutes": 90,
            "max_seats": 15,
            "enrolled_count": 6,
            "price_credits": 99.00,
        },
        {
            "title": "UI/UX Design Systems in Figma for Beginners",
            "instructor": teacher,
            "category": cat_design,
            "description": "Learn color theory, auto-layout 5.0, design tokens, interactive micro-animations, and wireframing.",
            "scheduled_at": now + datetime.timedelta(days=4, hours=3),
            "duration_minutes": 90,
            "max_seats": 15,
            "enrolled_count": 5,
            "price_credits": 85.00,
        },
        {
            "title": "Data Analysis with Pandas, NumPy & Matplotlib",
            "instructor": admin_instr or teacher,
            "category": cat_data,
            "description": "Master data wrangling, cleaning dirty datasets, exploratory data analysis (EDA), and stunning data visualizations.",
            "scheduled_at": now + datetime.timedelta(days=5, hours=6),
            "duration_minutes": 105,
            "max_seats": 18,
            "enrolled_count": 2,
            "price_credits": 110.00,
        },
        {
            "title": "Acoustic Guitar Chords & Fingerpicking for Beginners",
            "instructor": student_instr or teacher,
            "category": cat_music,
            "description": "Master open chords, smooth chord transitions, rhythm strumming patterns, and your first 5 full songs.",
            "scheduled_at": now + datetime.timedelta(days=6, hours=4),
            "duration_minutes": 60,
            "max_seats": 10,
            "enrolled_count": 3,
            "price_credits": 60.00,
        },
        {
            "title": "English Public Speaking & Professional Communication",
            "instructor": admin_instr or teacher,
            "category": cat_lang,
            "description": "Boost your confidence in presentations, tech interviews, and workplace discussions with live practice & feedback.",
            "scheduled_at": now + datetime.timedelta(days=7, hours=5),
            "duration_minutes": 75,
            "max_seats": 12,
            "enrolled_count": 4,
            "price_credits": 75.00,
        },
        {
            "title": "SQL & Relational Database Performance Tuning",
            "instructor": teacher,
            "category": cat_prog,
            "description": "Advanced SQL joins, indexing strategies, query execution plans, transactions, and database optimization.",
            "scheduled_at": now + datetime.timedelta(days=8, hours=3),
            "duration_minutes": 90,
            "max_seats": 16,
            "enrolled_count": 1,
            "price_credits": 95.00,
        },
    ]

    for bdata in new_batches_data:
        Batch.objects.get_or_create(
            title=bdata["title"],
            defaults=bdata
        )


def batches_view(request):
    """View to list all group batches / scheduled classes (like Lovable app)."""
    if Batch.objects.count() < 8:
        try:
            seed_rich_batches()
        except Exception as e:
            pass  # Seeding failures must never cause a 500

    category_id = request.GET.get('category')

    try:
        batches = list(Batch.objects.select_related('instructor', 'category').all())
        if category_id:
            batches = [b for b in batches if str(b.category_id) == str(category_id)]
    except Exception:
        batches = []

    try:
        categories = list(SkillCategory.objects.filter(is_active=True))
    except Exception:
        categories = []

    # User's enrolled batch IDs if authenticated
    enrolled_batch_ids = []
    if request.user.is_authenticated:
        try:
            enrolled_batch_ids = list(
                BatchEnrollment.objects.filter(student=request.user).values_list('batch_id', flat=True)
            )
        except Exception:
            enrolled_batch_ids = []

    return render(request, 'bookings/batches.html', {
        'batches': batches,
        'categories': categories,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
        'enrolled_batch_ids': enrolled_batch_ids,
    })


import uuid
from payments.models import Wallet, WalletTransaction, PaymentReceipt
from notifications.models import Notification


from django.db import transaction

@login_required
def join_batch(request, batch_id):
    """Enrolls current user in a group batch with mandatory payment processing."""
    try:
        batch = get_object_or_404(Batch.objects.select_related('instructor'), id=batch_id)

        # 1. Check if already enrolled
        already_enrolled = BatchEnrollment.objects.filter(batch=batch, student=request.user).exists()
        if already_enrolled:
            messages.info(request, f'You are already enrolled in batch "{batch.title}".')
            return redirect('/batches/')

        # 2. Check seat capacity
        if batch.enrolled_count >= batch.max_seats:
            messages.error(request, 'Sorry, this batch is already full!')
            return redirect('/batches/')

        price = Decimal(str(batch.price_credits or '0.00'))

        # 3. Check student's wallet balance
        student_wallet, _ = Wallet.objects.get_or_create(user=request.user)
        student_bal = Decimal(str(student_wallet.balance or '0.00'))

        if student_bal < price:
            messages.error(
                request,
                f'Insufficient balance (₹{student_bal:.2f}) to join "{batch.title}". '
                f'Batch fee is ₹{price:.2f}. Please add funds to your wallet.'
            )
            return redirect('/wallet/')

        # 4. Atomic Payment Processing & Enrollment
        with transaction.atomic():
            # Deduct from student
            student_wallet.balance = student_bal - price
            student_wallet.save()

            WalletTransaction.objects.create(
                wallet=student_wallet,
                amount=price,
                transaction_type='debit',
                description=f'Batch Enrollment Fee: {batch.title} (Instructor: {batch.instructor.username})'
            )

            # Credit to instructor
            instructor_wallet, _ = Wallet.objects.get_or_create(user=batch.instructor)
            inst_bal = Decimal(str(instructor_wallet.balance or '0.00'))
            inst_earned = Decimal(str(instructor_wallet.earned_total or '0.00'))

            instructor_wallet.balance = inst_bal + price
            instructor_wallet.earned_total = inst_earned + price
            instructor_wallet.save()

            WalletTransaction.objects.create(
                wallet=instructor_wallet,
                amount=price,
                transaction_type='credit',
                description=f'Earned from Batch Enrollment: {batch.title} (Student: {request.user.username})'
            )

            # Create Batch Enrollment
            BatchEnrollment.objects.create(batch=batch, student=request.user)
            batch.enrolled_count += 1
            batch.save()

            # Safe category name resolution
            cat_name = 'General'
            try:
                if batch.category:
                    cat_name = batch.category.category_name
            except Exception:
                cat_name = 'General'

            # Generate Payment Receipt
            tx_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            receipt = PaymentReceipt.objects.create(
                student=request.user,
                teacher=batch.instructor,
                batch=batch,
                item_title=batch.title,
                category_name=cat_name,
                amount=price,
                payment_method='Skill-Verse Wallet',
                transaction_id=tx_id,
                status='PAID'
            )

            receipt_num_str = str(receipt.receipt_number)

            # Notify Batch Teacher
            rec_num = receipt_num_str[:8]
            rec_url = f"/payments/receipt/{receipt_num_str}/"
            Notification.objects.create(
                user=batch.instructor,
                title=f"💳 Payment Received: ₹{price:.2f} from {request.user.username}",
                message=f"{request.user.username} enrolled in your batch '{batch.title}' and paid ₹{price:.2f}. Receipt #{rec_num} generated.",
                type="system",
                action_url=rec_url,
                action_text="View Payment Receipt",
                sender_name=request.user.username
            )

            # Notify Student
            Notification.objects.create(
                user=request.user,
                title=f"💳 Payment Receipt: ₹{price:.2f} for {batch.title}",
                message=f"You successfully joined '{batch.title}'. Payment of ₹{price:.2f} was deducted from your wallet.",
                type="booking",
                action_url=rec_url,
                action_text="View Receipt",
                sender_name="Skill-Verse System"
            )

        messages.success(
            request,
            f'Payment of ₹{price:.2f} successful! You have joined "{batch.title}".'
        )
        return redirect('receipt_detail', receipt_number=receipt_num_str)

    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Could not process batch enrollment: {str(e)}")
        return redirect('/batches/')



def live_sessions_view(request):
    """Unified Live Sessions hub — Doubt Calls tab + Live Video Room tab."""
    try:
        doubts = list(DoubtCall.objects.select_related('learner', 'mentor').all()[:15])
    except Exception:
        doubts = []
    return render(request, 'bookings/live_sessions.html', {
        'doubts': doubts,
    })


def doubt_view(request):
    """Backward-compatible redirect — now served by live_sessions_view."""
    from django.shortcuts import redirect as _redirect
    return _redirect('live_sessions')



@login_required
def create_doubt(request):
    """Create a new instant doubt call request (Fee: ₹50.00 per 15-min session)."""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        question = request.POST.get('question', '').strip()

        if subject and question:
            price = Decimal('50.00')
            admin_fee = Decimal('5.00')        # 10% platform fee
            teacher_earning = Decimal('45.00') # 90% to teacher

            # 1. Check Learner's Wallet
            from payments.models import Wallet, WalletTransaction, PaymentReceipt
            learner_wallet, _ = Wallet.objects.get_or_create(user=request.user)

            if learner_wallet.balance < price:
                messages.error(
                    request,
                    f'Insufficient wallet balance! A Doubt Call session costs ₹{price:.2f}. '
                    f'Your current balance is ₹{learner_wallet.balance:.2f}. Please add funds.'
                )
                return redirect('wallet')

            # 2. Deduct ₹50 from Learner's Wallet
            learner_wallet.balance = Decimal(str(learner_wallet.balance)) - price
            learner_wallet.save()

            WalletTransaction.objects.create(
                wallet=learner_wallet,
                amount=price,
                transaction_type='debit',
                description=f"Doubt Session Fee (15 min): '{subject}'"
            )

            # 3. Credit 10% Admin Fee (₹5.00)
            from django.contrib.auth.models import User
            admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
            if admin_user:
                admin_wallet, _ = Wallet.objects.get_or_create(user=admin_user)
                admin_wallet.balance = Decimal(str(admin_wallet.balance)) + admin_fee
                admin_wallet.earned_total = Decimal(str(admin_wallet.earned_total)) + admin_fee
                admin_wallet.save()

                WalletTransaction.objects.create(
                    wallet=admin_wallet,
                    amount=admin_fee,
                    transaction_type='credit',
                    description=f"Admin 10% Fee from Doubt Call by @{request.user.username}"
                )

            # 4. Create DoubtCall Record (uses built-in in-app room path, no external service)
            doubt = DoubtCall.objects.create(
                learner=request.user,
                subject=subject,
                question=question,
                status='searching',
                price=price,
                admin_fee=admin_fee,
                teacher_earning=teacher_earning,
                duration_minutes=15,
                is_paid=True,
                meeting_link=''
            )
            doubt.meeting_link = f'/bookings/room/{doubt.id}/'
            doubt.save(update_fields=['meeting_link'])

            # 5. Create Payment Receipt for Learner
            tx_id = f"TXN-DBT-{uuid.uuid4().hex[:8].upper()}"
            target_teacher = admin_user if admin_user else request.user
            receipt = PaymentReceipt.objects.create(
                student=request.user,
                teacher=target_teacher,
                item_title=f"15-Min Doubt Session: {subject}",
                category_name='Doubt Call',
                amount=price,
                payment_method='Skill-Verse Wallet',
                transaction_id=tx_id,
                status='PAID'
            )

            # 6. Notify Learner
            rec_num = str(receipt.receipt_number)[:8]
            Notification.objects.create(
                user=request.user,
                title=f"💳 Doubt Call Payment: ₹{price:.2f}",
                message=f"₹{price:.2f} deducted for 15-min Doubt Call '{subject}'. Receipt #{rec_num} generated.",
                type="booking",
                action_url=f"/payments/receipt/{receipt.receipt_number}/",
                action_text="View Receipt",
                sender_name="Skill-Verse System"
            )

            messages.success(
                request,
                f'Instant doubt call created! ₹{price:.2f} deducted from wallet. Teachers have been notified.'
            )
            return redirect('live_sessions')
        else:
            messages.error(request, 'Please provide subject and question.')

    return redirect('live_sessions')


@login_required
def live_room(request, room_id=None):
    """In-app live video room with camera, mic, screen share, 15-minute timer & payout."""
    from django.utils import timezone
    from payments.models import Wallet, WalletTransaction, PaymentReceipt

    room_name = f"Skill-VerseRoom-{room_id or 'General'}"
    doubt = None
    remaining_seconds = 900 # 15 minutes default
    is_doubt_session = False

    # Check if room_id is associated with a DoubtCall ID
    if room_id:
        try:
            doubt = DoubtCall.objects.select_related('learner', 'mentor').get(pk=room_id)
            is_doubt_session = True

            # If current user is not the learner and mentor is not assigned, assign mentor!
            if doubt.learner != request.user and not doubt.mentor:
                doubt.mentor = request.user
                doubt.status = 'active'

            # Set started_at if not set
            if not doubt.started_at:
                doubt.started_at = timezone.now()
                doubt.status = 'active'
                doubt.save()

            # Credit 90% (₹45.00) to Teacher / Mentor if not already credited
            if doubt.mentor and not doubt.is_teacher_paid:
                teacher_wallet, _ = Wallet.objects.get_or_create(user=doubt.mentor)
                teacher_wallet.balance = Decimal(str(teacher_wallet.balance)) + Decimal(str(doubt.teacher_earning))
                teacher_wallet.earned_total = Decimal(str(teacher_wallet.earned_total)) + Decimal(str(doubt.teacher_earning))
                teacher_wallet.save()

                WalletTransaction.objects.create(
                    wallet=teacher_wallet,
                    amount=doubt.teacher_earning,
                    transaction_type='credit',
                    description=f"Earned 90% (₹{doubt.teacher_earning:.2f}) from Doubt Session: '{doubt.subject}'"
                )

                doubt.is_teacher_paid = True
                doubt.save()

                # Update receipt teacher reference
                PaymentReceipt.objects.filter(item_title__icontains=doubt.subject).update(teacher=doubt.mentor)

                # Send Notification to Teacher
                Notification.objects.create(
                    user=doubt.mentor,
                    title=f"💳 ₹{doubt.teacher_earning:.2f} Credited to Wallet",
                    message=f"You joined Doubt Call '{doubt.subject}'. ₹{doubt.teacher_earning:.2f} (90% fee) has been credited to your wallet.",
                    type="booking",
                    sender_name=doubt.learner.username
                )

            # Calculate remaining seconds for 15-minute time limit
            total_allowed = doubt.duration_minutes * 60
            elapsed = (timezone.now() - doubt.started_at).total_seconds()
            remaining_seconds = max(0, int(total_allowed - elapsed))

            # If timer expired, complete doubt call & redirect out!
            if remaining_seconds <= 0:
                doubt.status = 'completed'
                doubt.ended_at = timezone.now()
                doubt.save()
                messages.info(request, "⏰ The 15-minute Doubt Call session time limit has expired.")
                return redirect('live_sessions')

        except (DoubtCall.DoesNotExist, ValueError):
            pass

    return render(request, 'bookings/live_room.html', {
        'room_name': room_name,
        'user_name': request.user.username,
        'doubt': doubt,
        'remaining_seconds': remaining_seconds,
        'is_doubt_session': is_doubt_session,
    })


from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def create_batch(request):
    """Create a new group batch session — Teacher/Admin only."""
    categories = SkillCategory.objects.filter(is_active=True)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        scheduled_at = request.POST.get('scheduled_at')
        duration_minutes = request.POST.get('duration_minutes', 60)
        max_seats = request.POST.get('max_seats', 15)
        price_credits = request.POST.get('price_credits', '50.00')
        meeting_link = request.POST.get('meeting_link', '').strip()

        errors = []
        if not title:
            errors.append('Batch title is required.')
        if not category_id:
            errors.append('Please select a category.')
        if not scheduled_at:
            errors.append('Scheduled date & time is required.')

        if not errors:
            try:
                category = SkillCategory.objects.get(id=category_id)
                batch = Batch.objects.create(
                    instructor=request.user,
                    title=title,
                    description=description,
                    category=category,
                    scheduled_at=scheduled_at,
                    duration_minutes=int(duration_minutes),
                    max_seats=int(max_seats),
                    price_credits=Decimal(str(price_credits)),
                    meeting_link=meeting_link,
                    status='upcoming',
                )
                messages.success(request, f'✅ Batch "{batch.title}" created successfully!')
                return redirect('batches')
            except Exception as e:
                errors.append(f'Error creating batch: {str(e)}')

        return render(request, 'bookings/create_batch.html', {
            'categories': categories,
            'errors': errors,
            'form_data': request.POST,
        })

    return render(request, 'bookings/create_batch.html', {
        'categories': categories,
        'errors': [],
        'form_data': {},
    })


@staff_member_required
def delete_batch(request, batch_id):
    """Delete a batch — Teacher (own) / Admin (any)."""
    batch = get_object_or_404(Batch, id=batch_id)
    if not request.user.is_superuser and batch.instructor != request.user:
        messages.error(request, 'You can only delete your own batches.')
        return redirect('batches')
    batch_title = batch.title
    batch.delete()
    messages.success(request, f'Batch "{batch_title}" deleted.')
    return redirect('batches')
