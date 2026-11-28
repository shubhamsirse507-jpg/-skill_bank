"""
Management command to seed QuestionBank and Question records
for common skills (Python/Django, UI/UX Design, Guitar, Data/SQL, Web Dev, Generic Teaching).
Seeds 36+ questions idempotently.
"""
from django.core.management.base import BaseCommand
from admin_panel.models import QuestionBank, Question


SEED_DATA = {
    'python': {
        'description': 'Python, Django & Backend Development',
        'questions': [
            (
                'What is the primary benefit of using an ORM like Django ORM?',
                'Eliminates the need for a database',
                'Maps database tables to Python classes and prevents SQL injection by default',
                'Automatically compiles Python to C++',
                'Replaces HTTP routing',
                'B',
                'ORMs abstract SQL queries into model methods and parameterize queries safely.',
            ),
            (
                'Which Python data structure preserves insertion order and provides O(1) average key lookup?',
                'list',
                'set',
                'dict',
                'tuple',
                'C',
                'Python 3.7+ dicts preserve insertion order and use hash tables for O(1) lookup.',
            ),
            (
                'In Django, what is the purpose of select_related()?',
                'To cache HTML templates in Redis',
                'To perform an SQL JOIN and fetch related ForeignKey/OneToOne objects in one query',
                'To paginate a queryset automatically',
                'To delete orphaned database rows',
                'B',
                'select_related() avoids N+1 query problems for single-valued relationships.',
            ),
            (
                'Which HTTP status code indicates a resource was successfully created?',
                '200 OK',
                '201 Created',
                '204 No Content',
                '302 Found',
                'B',
                '201 Created indicates a new resource has been created by a POST/PUT request.',
            ),
            (
                'Why should secrets like API keys never be committed to Git?',
                'Git rejects files larger than 1 KB',
                'Anyone with repo access or git history can extract and abuse them',
                'Python cannot read strings from tracked files',
                'It slows down Django migrations',
                'B',
                'Secrets in git history persist even after deletion; use environment variables.',
            ),
            (
                'What does @transaction.atomic in Django guarantee?',
                'All queries inside run asynchronously',
                'All DB operations inside succeed together or roll back on exception',
                'Queries bypass database locks',
                'Views automatically require login',
                'B',
                'transaction.atomic ensures ACID atomicity for a block of database operations.',
            ),
        ],
    },
    'design': {
        'description': 'UI/UX Design, Figma & Accessibility',
        'questions': [
            (
                'What does "Visual Hierarchy" refer to in UI design?',
                'Arranging elements by size, contrast, and spacing to guide attention',
                'Using only monochrome colors',
                'Exporting assets at 300 DPI',
                'Hiding navigation behind menus',
                'A',
                'Visual hierarchy helps users scan and understand importance immediately.',
            ),
            (
                'What is the minimum WCAG 2.1 AA contrast ratio for normal body text?',
                '2.0:1',
                '3.0:1',
                '4.5:1',
                '7.0:1',
                'C',
                'WCAG AA requires 4.5:1 for normal text and 3:1 for large text.',
            ),
            (
                'What is the main purpose of low-fidelity wireframes?',
                'Finalizing brand illustrations and gradients',
                'Validating layout, hierarchy, and user flows before visual polish',
                'Writing production CSS animations',
                'Testing server latency',
                'B',
                'Wireframes focus on structure and flow cheaply before high-fidelity UI.',
            ),
            (
                'In Figma, what is Auto Layout primarily used for?',
                'Generating SQL schemas',
                'Creating responsive frames that adapt automatically when content changes',
                'Compressing PNG exports',
                'Recording user interviews',
                'B',
                'Auto Layout works like CSS Flexbox for responsive components.',
            ),
            (
                'Which research method observes real users completing tasks to uncover friction?',
                'Usability testing',
                'A/B color voting',
                'Mood boarding',
                'Code minification',
                'A',
                'Usability testing reveals where users get confused in real workflows.',
            ),
            (
                'Why is a minimum 44x44px touch target recommended on mobile?',
                'To match desktop monitor DPI',
                'To prevent mis-taps and improve accessibility for all finger sizes',
                'To increase page load speed',
                'To satisfy browser CORS rules',
                'B',
                'Adequate touch targets reduce accidental taps on touchscreens.',
            ),
        ],
    },
    'guitar': {
        'description': 'Acoustic & Electric Guitar',
        'questions': [
            (
                'What is the standard tuning of a 6-string guitar from lowest (6th) to highest (1st) string?',
                'E A D G B E',
                'D A D G A D',
                'E B G D A E',
                'C G D A E B',
                'A',
                'Standard tuning from 6th (thickest) to 1st (thinnest) string is E-A-D-G-B-E.',
            ),
            (
                'What does a capo do when clamped onto the 2nd fret?',
                'Lowers pitch by a whole step',
                'Raises the open-string pitch by two semitones (one whole step)',
                'Mutes all strings permanently',
                'Changes a 6-string into a bass guitar',
                'B',
                'Each fret raises pitch by one semitone; fret 2 raises open strings by 2 semitones.',
            ),
            (
                'Which three notes form a C Major triad?',
                'C - Eb - G',
                'C - E - G',
                'C - F - G',
                'C - E - B',
                'B',
                'A major triad consists of root (1), major third (3), and perfect fifth (5).',
            ),
            (
                'When teaching a beginner their first open chords, what reduces finger buzz?',
                'Placing fingertips right behind the fret wire with arched fingers',
                'Pressing directly on top of the metal fret',
                'Flattening all fingers across adjacent strings',
                'Detuning the strings completely',
                'A',
                'Pressing just behind the fret wire requires less force and produces a clean note.',
            ),
            (
                'What is the most effective way for a beginner to build strumming rhythm?',
                'Practicing slowly with a metronome and keeping the strumming hand moving steadily',
                'Playing as fast as possible from day one',
                'Only practicing downstrokes without counting',
                'Ignoring tempo variations',
                'A',
                'A steady pendulum motion with a metronome builds internal timing.',
            ),
            (
                'Which chord progression is known as the I-V-vi-IV progression in the key of G Major?',
                'G - D - Em - C',
                'G - C - D - Am',
                'G - Am - Bm - C',
                'G - Em - C - D',
                'A',
                'In G major: I=G, V=D, vi=Em, IV=C.',
            ),
        ],
    },
    'data': {
        'description': 'Data Science, SQL & Analytics',
        'questions': [
            (
                'Which SQL clause filters groups created by GROUP BY?',
                'WHERE',
                'HAVING',
                'ORDER BY',
                'DISTINCT',
                'B',
                'WHERE filters rows before grouping; HAVING filters aggregated groups.',
            ),
            (
                'In machine learning, what does overfitting mean?',
                'The model performs poorly on training data',
                'The model memorizes training noise and generalizes poorly to unseen data',
                'The dataset has too few columns',
                'The learning rate is too small',
                'B',
                'Overfitting occurs when a model fits training quirks rather than general patterns.',
            ),
            (
                'Why do we split data into train, validation, and test sets?',
                'To reduce file size on disk',
                'To tune hyperparameters without leaking test set information',
                'Because pandas cannot load full CSVs',
                'To remove all missing values automatically',
                'B',
                'A held-out test set gives an unbiased estimate of generalization.',
            ),
            (
                'Which metric is most informative for an imbalanced binary classification dataset (e.g. 1% fraud)?',
                'Accuracy alone',
                'Precision, Recall, and F1 / PR-AUC',
                'Mean Squared Error',
                'R-squared',
                'B',
                'A trivial model predicting all 0s gets 99% accuracy; Precision/Recall capture minority class performance.',
            ),
            (
                'What does INNER JOIN return in SQL?',
                'All rows from the left table regardless of match',
                'Only rows with matching keys in both tables',
                'Every possible Cartesian combination',
                'Only unmatched rows',
                'B',
                'INNER JOIN returns rows where the join condition matches in both tables.',
            ),
            (
                'In pandas, which method fills missing NaN values with a specified value?',
                'dropna()',
                'fillna()',
                'isna()',
                'groupby()',
                'B',
                'fillna() replaces NaN values; dropna() removes rows/columns with NaN.',
            ),
        ],
    },
    'web': {
        'description': 'HTML, CSS, JavaScript & Frontend',
        'questions': [
            (
                'What is the purpose of semantic HTML elements like <nav>, <main>, and <article>?',
                'They automatically style elements with Flexbox',
                'They convey document structure to browsers, screen readers, and SEO',
                'They replace the need for JavaScript',
                'They prevent XSS attacks',
                'B',
                'Semantic tags improve accessibility and machine readability.',
            ),
            (
                'In CSS, which property controls alignment along the main axis in a flex container?',
                'align-items',
                'justify-content',
                'flex-wrap',
                'grid-gap',
                'B',
                'justify-content aligns items along the main axis; align-items along the cross axis.',
            ),
            (
                'What is event delegation in JavaScript?',
                'Attaching one listener to a parent element to handle events from child elements via bubbling',
                'Canceling all browser default events',
                'Running click handlers inside a Web Worker',
                'Reloading the page on every click',
                'A',
                'Event delegation saves memory and handles dynamically added child elements.',
            ),
            (
                'Why should user-supplied strings be inserted via textContent instead of innerHTML?',
                'textContent is faster for CSS animations',
                'textContent prevents Cross-Site Scripting (XSS) by not parsing HTML/scripts',
                'innerHTML does not work in Chrome',
                'textContent automatically translates text',
                'B',
                'innerHTML parses HTML and can execute injected scripts; textContent treats input as plain text.',
            ),
            (
                'What does the HTTP header Content-Security-Policy (CSP) help mitigate?',
                'Slow DNS resolution',
                'Cross-Site Scripting (XSS) and unauthorized script execution',
                'Database deadlocks',
                'Expired TLS certificates',
                'B',
                'CSP restricts which scripts, styles, and origins the browser may load/execute.',
            ),
            (
                'Which array method in JavaScript creates a new array with elements that pass a test?',
                'forEach()',
                'filter()',
                'push()',
                'splice()',
                'B',
                'filter() returns a new array of matching elements without mutating the original.',
            ),
        ],
    },
    'generic': {
        'description': 'Pedagogy & Live Teaching Best Practices',
        'questions': [
            (
                'What is the best first step when onboarding a new student in a 1-on-1 lesson?',
                'Assess their current knowledge, goals, and preferred pace',
                'Jump straight into advanced material',
                'Give them a 50-page PDF without context',
                'Skip introductions to save 2 minutes',
                'A',
                'Baseline assessment ensures the lesson matches the learner.',
            ),
            (
                'How should a 60-minute live teaching session ideally be structured?',
                'Goal recap -> guided demonstration -> hands-on practice -> summary & next steps',
                '60 minutes of uninterrupted slides',
                '50 minutes of silence while the student reads',
                'Random topics with no agenda',
                'A',
                'Active practice paired with clear goals yields strong retention.',
            ),
            (
                'If a student is stuck on a concept, what is the most effective response?',
                'Offer a simpler analogy and walk through a small example together',
                'Repeat the exact same explanation louder',
                'Tell them to look it up after class',
                'Move on without checking understanding',
                'A',
                'Alternative framing and scaffolding resolve confusion quickly.',
            ),
            (
                'What makes feedback actionable for a learner?',
                'Pointing out the specific issue, why it matters, and how to fix it',
                'Saying "good job" regardless of errors',
                'Saying "that is wrong" with no explanation',
                'Waiting until the end of the month',
                'A',
                'Specific, timely guidance lets students correct habits immediately.',
            ),
            (
                'Why is checking for understanding mid-lesson important?',
                'It catches misconceptions early before building more complex concepts on top',
                'It replaces the need for lesson planning',
                'It is only useful for grading exams',
                'It prevents students from asking questions',
                'A',
                'Formative checks keep the lesson aligned with the learner.',
            ),
            (
                'How should you handle a student who asks a question outside your prepared slides?',
                'Acknowledge it, answer concisely if relevant, or note it for follow-up if out of scope',
                'Ignore the question',
                'End the call immediately',
                'Guess confidently even if unsure',
                'A',
                'Honesty and structured follow-up build trust with learners.',
            ),
        ],
    },
}


class Command(BaseCommand):
    help = "Seed QuestionBank and Question records (36 questions across 6 banks)."

    def handle(self, *args, **options):
        created_banks = 0
        created_questions = 0

        for slug, data in SEED_DATA.items():
            bank, b_created = QuestionBank.objects.get_or_create(
                skill_slug=slug,
                defaults={'description': data['description']},
            )
            if b_created:
                created_banks += 1

            for q_text, a, b, c, d, correct, expl in data['questions']:
                _, q_created = Question.objects.get_or_create(
                    bank=bank,
                    question_text=q_text,
                    defaults={
                        'option_a': a,
                        'option_b': b,
                        'option_c': c,
                        'option_d': d,
                        'correct_option': correct,
                        'explanation': expl,
                    },
                )
                if q_created:
                    created_questions += 1

        total_q = Question.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Question bank seeded: +{created_banks} bank(s), +{created_questions} question(s) (total={total_q})."
        ))
