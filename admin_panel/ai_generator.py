"""
admin_panel/ai_generator.py

Question selector & shuffler for Teacher Qualification Exams.
- Uses whole-word matching (regex \b...\b) so 'ui' never matches 'guitar'.
- Draws from DB QuestionBank/Question when seeded, with a generic teaching fallback.
- Shuffles both question order and option order per test.
"""
import random
import re

# Whole-word keyword sets for fallback matching
_CATEGORY_PATTERNS = {
    'python': re.compile(r'\b(python|django|flask|fastapi|backend|coding|programming|software)\b', re.IGNORECASE),
    'design': re.compile(r'\b(ui|ux|ui/ux|figma|design|wireframe|typography|photoshop|illustrator)\b', re.IGNORECASE),
    'guitar': re.compile(r'\b(guitar|acoustic|electric guitar|ukulele|chords|music)\b', re.IGNORECASE),
    'data': re.compile(r'\b(data|sql|analytics|pandas|machine learning|ai|ml|statistics)\b', re.IGNORECASE),
    'web': re.compile(r'\b(html|css|javascript|react|node|frontend|web development)\b', re.IGNORECASE),
}


def _whole_word_match(slug: str, text: str) -> bool:
    if not slug or not text:
        return False
    pattern = re.compile(r'\b' + re.escape(slug.strip().lower()) + r'\b', re.IGNORECASE)
    return bool(pattern.search(text))


def _shuffle_question_options(q_dict: dict, idx: int) -> dict:
    """
    Given a question dict with options {'A': ..., 'B': ..., 'C': ..., 'D': ...} and 'correct' letter,
    shuffle the 4 option texts and remap 'correct' to the new letter.
    """
    opts = q_dict['options']
    correct_letter = q_dict['correct']
    correct_text = opts[correct_letter]

    texts = [opts['A'], opts['B'], opts['C'], opts['D']]
    random.shuffle(texts)
    letters = ['A', 'B', 'C', 'D']
    new_opts = dict(zip(letters, texts))
    new_correct = next(k for k, v in new_opts.items() if v == correct_text)

    return {
        'id': idx,
        'source_id': q_dict.get('source_id'),
        'question': q_dict['question'],
        'options': new_opts,
        'correct': new_correct,
        'explanation': q_dict.get('explanation', ''),
    }


def _generic_fallback_questions(skill_name: str):
    """Generic teaching & pedagogy fallback when no DB bank exists."""
    return [
        {
            'question': f'When teaching {skill_name} to a beginner, what is the best first step?',
            'options': {
                'A': 'Assess their current level and set clear, achievable milestones',
                'B': 'Assign an advanced project without explanation',
                'C': 'Skip foundational concepts to save time',
                'D': 'Provide only unannotated reference links',
            },
            'correct': 'A',
            'explanation': 'Assessing baseline knowledge lets you tailor pacing and examples.',
        },
        {
            'question': f'How should you structure a 60-minute live 1-on-1 session for {skill_name}?',
            'options': {
                'A': '10m recap & goals -> 35m guided practice -> 15m Q&A and next steps',
                'B': '60m uninterrupted monologue',
                'C': '55m Q&A with no demonstration',
                'D': 'Unplanned casual chat',
            },
            'correct': 'A',
            'explanation': 'A clear structure balances explanation, hands-on practice, and feedback.',
        },
        {
            'question': f'If a student repeatedly struggles with a core concept in {skill_name}, what should you do?',
            'options': {
                'A': 'Break it down into smaller steps using a concrete analogy',
                'B': 'Tell them to figure it out on their own',
                'C': 'Move to harder topics immediately',
                'D': 'End the session early',
            },
            'correct': 'A',
            'explanation': 'Scaffolding and analogies help learners bridge conceptual gaps.',
        },
        {
            'question': 'Which feedback style most effectively helps learners improve?',
            'options': {
                'A': 'Specific, actionable, and encouraging feedback tied to examples',
                'B': 'Vague praise with no specifics',
                'C': 'Harsh criticism without guidance',
                'D': 'Waiting weeks before mentioning mistakes',
            },
            'correct': 'A',
            'explanation': 'Actionable, timely feedback accelerates skill acquisition.',
        },
        {
            'question': 'What is the primary purpose of a formative check-in during a lesson?',
            'options': {
                'A': 'Verify understanding early so misconceptions are fixed right away',
                'B': 'Assign a final pass/fail grade mid-lesson',
                'C': 'Fill extra time at the end',
                'D': 'Avoid answering student questions',
            },
            'correct': 'A',
            'explanation': 'Formative checks catch misunderstandings before they compound.',
        },
    ]


def draw_questions_for_skill(skill=None, skill_name: str = '', count: int = 10,
                             skill_level: str = 'Intermediate') -> list:
    """
    Draw `count` randomized, option-shuffled questions for a Skill (or skill_name).
    Uses DB QuestionBank/Question first (matched by FK or whole-word slug),
    topping up from the generic teaching bank if needed.
    """
    from .models import QuestionBank, Question

    title = skill.title if skill else (skill_name or 'General Teaching')
    category_name = skill.category.category_name if (skill and skill.category) else ''
    search_text = f"{title} {category_name}".strip()

    matched_questions = []

    # 1. Exact FK match on QuestionBank
    if skill is not None:
        qs = Question.objects.filter(bank__skill=skill)
        matched_questions.extend(list(qs))

    # 2. Whole-word slug match across QuestionBanks (excluding 'generic')
    if len(matched_questions) < count:
        for bank in QuestionBank.objects.exclude(skill_slug='generic'):
            if _whole_word_match(bank.skill_slug, search_text):
                matched_questions.extend(list(bank.questions.all()))
            else:
                pat = _CATEGORY_PATTERNS.get(bank.skill_slug)
                if pat and pat.search(search_text):
                    matched_questions.extend(list(bank.questions.all()))

    # Deduplicate by Question.id
    seen_ids = set()
    unique_qs = []
    for q in matched_questions:
        if q.id not in seen_ids:
            seen_ids.add(q.id)
            unique_qs.append(q)

    # 3. Top up from 'generic' QuestionBank if needed
    if len(unique_qs) < count:
        generic_qs = Question.objects.filter(bank__skill_slug='generic').exclude(id__in=seen_ids)
        unique_qs.extend(list(generic_qs))

    random.shuffle(unique_qs)
    selected = unique_qs[:count]

    result = []
    for idx, q in enumerate(selected, start=1):
        raw = {
            'source_id': q.id,
            'question': q.question_text,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c,
                'D': q.option_d,
            },
            'correct': q.correct_option,
            'explanation': q.explanation,
        }
        result.append(_shuffle_question_options(raw, idx))

    # 4. If DB has not been seeded at all, use generic fallback
    if not result:
        fallback = _generic_fallback_questions(title)
        random.shuffle(fallback)
        for idx, raw in enumerate(fallback[:count], start=1):
            result.append(_shuffle_question_options(raw, idx))

    return result


def generate_ai_mock_test(skill_name, skill_level='Intermediate', count=5):
    """Backwards-compatible wrapper using whole-word matching & shuffling."""
    return draw_questions_for_skill(skill=None, skill_name=skill_name,
                                    count=count, skill_level=skill_level)
