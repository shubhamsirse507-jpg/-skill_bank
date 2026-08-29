// SkillBank Dashboard Interactivity & Animation Suite
document.addEventListener('DOMContentLoaded', function () {
    console.log('SkillBank Dashboard Engine Initialized.');

    // 1. Dynamic Time-Of-Day Greeting
    const greetingEl = document.getElementById('dynamicGreeting');
    if (greetingEl) {
        const hour = new Date().getHours();
        let greeting = 'Welcome back';
        let icon = '👋';
        if (hour >= 5 && hour < 12) {
            greeting = 'Good Morning';
            icon = '☀️';
        } else if (hour >= 12 && hour < 17) {
            greeting = 'Good Afternoon';
            icon = '⛅';
        } else if (hour >= 17 && hour < 22) {
            greeting = 'Good Evening';
            icon = '🌆';
        } else {
            greeting = 'Good Night';
            icon = '🌙';
        }
        greetingEl.innerHTML = `${greeting}, <span style="color:#0c6c63;">${greetingEl.dataset.username || 'Learner'}</span>! ${icon}`;
    }

    // 2. Daily Skill Inspiration Quote Rotator
    const quotes = [
        "\"The beautiful thing about learning is that no one can take it away from you.\" — B.B. King",
        "\"In learning you will teach, and in teaching you will learn.\" — Phil Collins",
        "\"Share your knowledge. It is a way to achieve immortality.\" — Dalai Lama",
        "\"Everyone you will ever meet knows something you don't.\" — Bill Nye",
        "\"Knowledge increases by sharing, not by saving.\" — Kamari aka Lyrikal"
    ];

    const quoteTextEl = document.getElementById('dailyQuoteText');
    const quoteBtn = document.getElementById('quoteRefreshBtn');
    let currentQuoteIndex = 0;

    function rotateQuote() {
        if (!quoteTextEl) return;
        quoteTextEl.style.opacity = '0';
        setTimeout(() => {
            currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
            quoteTextEl.textContent = quotes[currentQuoteIndex];
            quoteTextEl.style.opacity = '1';
        }, 200);
    }

    if (quoteBtn) {
        quoteBtn.addEventListener('click', rotateQuote);
    }

    // 3. Stat Card Numbers Count-Up Animation
    const statNumbers = document.querySelectorAll('.stat-count');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-target') || stat.textContent, 10);
        if (isNaN(target) || target === 0) return;

        const duration = 1200;
        const start = performance.now();

        function countStep(time) {
            const elapsed = time - start;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(easeOut * target);

            stat.textContent = current;
            if (progress < 1) {
                requestAnimationFrame(countStep);
            }
        }
        requestAnimationFrame(countStep);
    });

    // 4. Interactive 3D Card Hover Tilt Micro-Interactions
    const tiltCards = document.querySelectorAll('.stat-card-pro, .category-card-pro, .community-skill-card');
    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
});
