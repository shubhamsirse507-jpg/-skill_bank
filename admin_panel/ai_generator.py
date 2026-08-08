"""
admin_panel/ai_generator.py

AI Mock Test Question Generator for Teacher Qualification.
Dynamically constructs 5 skill-tailored multiple choice questions (MCQs)
based on the teacher's skill title, level, and description.
"""

def generate_ai_mock_test(skill_name, skill_level='Intermediate'):
    """
    Generates a structured list of 5 multiple choice questions.
    """
    s_clean = skill_name.strip().lower()
    
    if 'python' in s_clean or 'django' in s_clean or 'backend' in s_clean or 'code' in s_clean or 'programming' in s_clean:
        return [
            {
                "id": 1,
                "question": f"In {skill_name}, what is the primary benefit of using Object-Relational Mapping (ORM)?",
                "options": [
                    "A. Eliminates the need for a web server",
                    "B. Allows database interaction using object-oriented code instead of raw SQL",
                    "C. Speeds up CSS rendering in the browser",
                    "D. Automatically compiles code to machine binary"
                ],
                "correct": "B",
                "explanation": "ORM abstracts raw database SQL queries into object-oriented model methods."
            },
            {
                "id": 2,
                "question": f"Which status code represents a successful REST API request in {skill_name}?",
                "options": ["A. 404 Not Found", "B. 500 Server Error", "C. 200 OK", "D. 301 Redirect"],
                "correct": "C",
                "explanation": "HTTP status 200 OK indicates successful request completion."
            },
            {
                "id": 3,
                "question": f"When handling asynchronous tasks or background jobs, which pattern is recommended?",
                "options": [
                    "A. Blocking the main HTTP event loop thread",
                    "B. Offloading to background message queues / workers",
                    "C. Infinite while loops in global scope",
                    "D. Disabling database transactions"
                ],
                "correct": "B",
                "explanation": "Message queues handle long-running operations asynchronously without blocking HTTP response threads."
            },
            {
                "id": 4,
                "question": f"What is the role of virtual environments when teaching {skill_name}?",
                "options": [
                    "A. Isolating project-specific dependencies and packages",
                    "B. Increasing hardware CPU speed",
                    "C. Encrypting source code repository",
                    "D. Styling frontend components"
                ],
                "correct": "A",
                "explanation": "Virtual environments prevent dependency version conflicts between different projects."
            },
            {
                "id": 5,
                "question": f"What is a critical security practice when deploying a {skill_name} application?",
                "options": [
                    "A. Hardcoding API secret keys directly in public git repos",
                    "B. Keeping DEBUG=True in production settings",
                    "C. Storing sensitive credentials in environment variables (.env)",
                    "D. Disabling CORS protection"
                ],
                "correct": "C",
                "explanation": "Environment variables keep secret keys out of version control systems."
            }
        ]

    elif 'design' in s_clean or 'ui' in s_clean or 'ux' in s_clean or 'figma' in s_clean:
        return [
            {
                "id": 1,
                "question": f"In {skill_name}, what does the term 'Visual Hierarchy' refer to?",
                "options": [
                    "A. Arranging UI elements to guide the user's eye in order of importance",
                    "B. Using only dark colors across all screens",
                    "C. Increasing file size for print resolution",
                    "D. Writing CSS code manually without tools"
                ],
                "correct": "A",
                "explanation": "Visual hierarchy uses size, contrast, and layout to establish element importance."
            },
            {
                "id": 2,
                "question": "Which color contrast ratio is minimum required by WCAG AA standards for normal body text?",
                "options": ["A. 1:1", "B. 2:1", "C. 4.5:1", "D. 10:1"],
                "correct": "C",
                "explanation": "WCAG 2.1 AA requires a contrast ratio of at least 4.5:1 for standard body text."
            },
            {
                "id": 3,
                "question": "What is the primary goal of creating Wireframes during the UI/UX design phase?",
                "options": [
                    "A. Finalizing brand photography and illustrations",
                    "B. Establishing content layout, structure, and basic user flows",
                    "C. Writing backend database schemas",
                    "D. Animating micro-interactions"
                ],
                "correct": "B",
                "explanation": "Wireframes focus on structure and flow before visual polish is added."
            },
            {
                "id": 4,
                "question": "What is Figma's 'Auto Layout' feature used for?",
                "options": [
                    "A. Auto-generating backend APIs",
                    "B. Creating responsive components that automatically adjust to content size",
                    "C. Exporting video animations",
                    "D. Spell checking design text"
                ],
                "correct": "B",
                "explanation": "Auto Layout creates dynamic frames that resize based on inner element padding and content."
            },
            {
                "id": 5,
                "question": "In UX research, what is a 'Usability Test'?",
                "options": [
                    "A. Testing server RAM performance under high load",
                    "B. Observing real users as they complete tasks using the interface prototype",
                    "C. Calculating font licensing costs",
                    "D. Running automated unit test suites"
                ],
                "correct": "B",
                "explanation": "Usability testing evaluates the user experience by watching users complete actual tasks."
            }
        ]

    else:
        # General / Universal Skill Qualification Test
        return [
            {
                "id": 1,
                "question": f"When teaching {skill_name} to a beginner, what is the most effective introductory approach?",
                "options": [
                    "A. Explaining advanced theoretical edge cases before fundamentals",
                    "B. Breaking concepts down into small practical steps with hands-on exercises",
                    "C. Reading documentation aloud for 2 hours",
                    "D. Expecting complete mastery without feedback"
                ],
                "correct": "B",
                "explanation": "Hands-on progressive learning helps students build confidence and retain skills."
            },
            {
                "id": 2,
                "question": f"How do you assess student comprehension during a live {skill_name} session?",
                "options": [
                    "A. Asking targeted Q&A and requesting a quick practical demonstration",
                    "B. Assuming understanding if the student remains silent",
                    "C. Skipping live interaction",
                    "D. Only giving a final exam at the end of the year"
                ],
                "correct": "A",
                "explanation": "Interactive Q&A and real-time demonstrations allow immediate feedback and correction."
            },
            {
                "id": 3,
                "question": f"What is the best way to structure a 60-minute 1-on-1 teaching session for {skill_name}?",
                "options": [
                    "A. 10m review & objective -> 35m core demonstration -> 15m Q&A & practice",
                    "B. 60m continuous lecture without breaks",
                    "C. 55m Q&A -> 5m summary",
                    "D. Unstructured casual conversation"
                ],
                "correct": "A",
                "explanation": "A structured session ensures learning goals are set, demonstrated, and practiced."
            },
            {
                "id": 4,
                "question": "What key quality distinguishes an exceptional SkillBank teacher?",
                "options": [
                    "A. High subject authority, patience, clear communication, and structured guidance",
                    "B. Speaking as fast as possible to cover more topics",
                    "C. Rejecting questions during live calls",
                    "D. Teaching without preparation"
                ],
                "correct": "A",
                "explanation": "Clear communication, patience, and subject expertise drive successful student outcomes."
            },
            {
                "id": 5,
                "question": f"If a student struggles with a core concept in {skill_name}, what should the teacher do?",
                "options": [
                    "A. Provide an alternative visual or real-world analogy and simplify the problem",
                    "B. Tell the student to figure it out on their own",
                    "C. Skip the topic entirely",
                    "D. End the session immediately"
                ],
                "correct": "A",
                "explanation": "Re-framing concepts using analogies helps bridge gaps in understanding."
            }
        ]
