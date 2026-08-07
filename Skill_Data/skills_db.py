# Comprehensive Skill Knowledge Base for Skill Bank AI

SKILL_KNOWLEDGE_BASE = {
    "python": {
        "title": "Python Programming",
        "category": "Programming & Development",
        "description": "High-level, interpreted language known for readability, versatility, and rich ecosystem.",
        "roadmap": ["Variables & Data Types", "Control Flow & Loops", "Functions & Modules", "OOP (Classes/Objects)", "File I/O & Exception Handling", "Virtual Environments", "Frameworks (Django/Flask/FastAPI)", "Data Science & AI (Pandas, NumPy, PyTorch)"],
        "popular_frameworks": ["Django", "Flask", "FastAPI", "Pandas", "NumPy", "PyTorch", "TensorFlow", "Scikit-Learn"],
        "project_ideas": ["REST API with Django", "Web Scraper", "AI Chatbot", "Automated Task Scheduler", "Data Analysis Dashboard"],
        "interview_questions": [
            "Difference between list and tuple?",
            "What are Python decorators and generator functions?",
            "Explain GIL (Global Interpreter Lock).",
            "Difference between args and kwargs?"
        ]
    },
    "javascript": {
        "title": "JavaScript & Web Development",
        "category": "Frontend & Full Stack",
        "description": "The language of the web, powering interactive frontends and backend servers via Node.js.",
        "roadmap": ["JS Syntax & ES6+ Features", "DOM Manipulation & Events", "Promises, Async/Await & Fetch API", "Node.js & Express Basics", "Frontend Framework (React, Vue, Next.js)", "TypeScript Integration", "State Management (Redux/Zustand)"],
        "popular_frameworks": ["React.js", "Next.js", "Vue.js", "Node.js", "Express.js", "TypeScript", "TailwindCSS"],
        "project_ideas": ["Real-time Chat App (Socket.io)", "E-commerce Frontend", "Task Management Kanban Board", "Weather Dashboard"],
        "interview_questions": [
            "Explain closures and scope in JS.",
            "Difference between var, let, and const.",
            "What is the Event Loop and Call Stack?",
            "Difference between == and ===?"
        ]
    },
    "django": {
        "title": "Django Framework",
        "category": "Backend Web Development",
        "description": "The web framework for perfectionists with deadlines — battery-included Python framework.",
        "roadmap": ["MVT Architecture", "URL Routing & Views", "Django ORM & Models", "Templates & Static Files", "Django Forms & Authentication", "Django REST Framework (DRF)", "Middleware & Signals", "Deployment (Gunicorn, Nginx, PostgreSQL)"],
        "popular_frameworks": ["Django REST Framework (DRF)", "Django Channels (WebSockets)", "Celery (Background Tasks)", "Django Allauth"],
        "project_ideas": ["Skill Bank Platform", "Social Media Backend", "Blog with Markdown & Auth", "Multi-vendor Marketplace"],
        "interview_questions": [
            "What is MVT architecture in Django?",
            "Difference between select_related and prefetch_related?",
            "How does Django migration system work?",
            "What are signals in Django?"
        ]
    },
    "react": {
        "title": "React.js Frontend Development",
        "category": "Frontend Development",
        "description": "A popular JavaScript library for building component-based user interfaces.",
        "roadmap": ["JSX Syntax", "Components (Functional & Class)", "Props & State", "Hooks (useState, useEffect, useContext, useMemo)", "React Router", "API Integration", "State Management", "Next.js (SSR/SSG)"],
        "popular_frameworks": ["Next.js", "Redux Toolkit", "Zustand", "Tailwind CSS", "Material UI", "Shadcn UI"],
        "project_ideas": ["Portfolio Website", "Movie Browsing App", "Crypto Tracker Dashboard", "AI Image Generator Interface"],
        "interview_questions": [
            "What is Virtual DOM and how does reconciliation work?",
            "Difference between props and state?",
            "What are custom hooks?",
            "How do useEffect dependency arrays work?"
        ]
    },
    "html_css": {
        "title": "HTML5 & CSS3 Design System",
        "category": "Web Fundamentals & UI/UX",
        "description": "Building blocks of the web for structuring and styling modern responsive websites.",
        "roadmap": ["Semantic HTML5 Tags", "CSS Box Model & Typography", "Flexbox Layout", "CSS Grid Layout", "Responsive Web Design (Media Queries)", "CSS Animations & Keyframes", "Glassmorphic & Dark UI Design", "Tailwind CSS"],
        "popular_frameworks": ["Tailwind CSS", "Bootstrap", "Sass/SCSS", "PostCSS"],
        "project_ideas": ["Responsive Landing Page", "CSS Art & Animation", "UI Component Library"],
        "interview_questions": [
            "Difference between display: flex and display: grid?",
            "What is CSS specificity?",
            "Difference between em, rem, and px?"
        ]
    },
    "sql_database": {
        "title": "SQL & Relational Databases",
        "category": "Database Engineering",
        "description": "Structured Query Language for managing relational databases like PostgreSQL, MySQL, SQLite.",
        "roadmap": ["Relational DB Concepts", "SELECT, WHERE, JOIN Queries", "GROUP BY, HAVING & Aggregations", "Database Indexing & Normalization (1NF, 2NF, 3NF)", "Transactions & ACID Properties", "Stored Procedures & Triggers"],
        "popular_frameworks": ["PostgreSQL", "MySQL", "SQLite", "SQLAlchemy", "Django ORM"],
        "project_ideas": ["Library Management DB", "E-commerce DB Schema", "Analytics Data Warehouse"],
        "interview_questions": [
            "Difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN?",
            "What are ACID properties?",
            "What is database indexing and how does it improve query speed?"
        ]
    },
    "machine_learning": {
        "title": "Machine Learning & AI",
        "category": "Data Science & AI",
        "description": "Algorithms and statistical models that enable computers to learn from data.",
        "roadmap": ["Math Fundamentals (Linear Algebra, Calculus, Statistics)", "Data Preprocessing & EDA", "Supervised Learning (Regression, Classification)", "Unsupervised Learning (K-Means, PCA)", "Model Evaluation & Hyperparameter Tuning", "Deep Learning (Neural Networks, PyTorch/TensorFlow)", "LLMs & Prompt Engineering"],
        "popular_frameworks": ["Scikit-Learn", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Hugging Face"],
        "project_ideas": ["House Price Prediction", "Spam Email Classifier", "Sentiment Analysis Tool", "Object Detection with OpenCV"],
        "interview_questions": [
            "Difference between Supervised and Unsupervised learning?",
            "What is Overfitting and how do you prevent it?",
            "Explain Precision, Recall, and F1-Score."
        ]
    },
    "devops_cloud": {
        "title": "DevOps & Cloud Engineering",
        "category": "Infrastructure & Operations",
        "description": "Practices combining software development and IT operations to shorten lifecycle delivery.",
        "roadmap": ["Linux CLI & Bash Scripting", "Git Version Control & CI/CD Pipelines", "Docker Containerization", "Kubernetes Orchestration", "Cloud Platforms (AWS/GCP/Azure)", "Infrastructure as Code (Terraform)"],
        "popular_frameworks": ["Docker", "Kubernetes", "AWS", "GitHub Actions", "Terraform", "Nginx"],
        "project_ideas": ["Automated CI/CD Pipeline for Django App", "Dockerized Microservices", "AWS ECS Deployment"],
        "interview_questions": [
            "What is Docker containerization vs Virtual Machines?",
            "How does CI/CD improve software release cycles?",
            "What is Nginx reverse proxy?"
        ]
    },
    "git_github": {
        "title": "Git & Version Control",
        "category": "Software Engineering Tools",
        "description": "Distributed version control system for tracking changes in source code.",
        "roadmap": ["Git Basics (init, add, commit, status)", "Branching & Merging (checkout, merge, rebase)", "Remote Repos (push, pull, clone)", "Pull Requests & Code Reviews", "Resolving Merge Conflicts", "Git Stash, Cherry-pick & Tagging"],
        "popular_frameworks": ["Git", "GitHub", "GitLab", "Bitbucket"],
        "project_ideas": ["Open Source Contribution", "Git Branching Workflow Practice"],
        "interview_questions": [
            "Difference between git merge and git rebase?",
            "How do you resolve a merge conflict?",
            "What is git stash used for?"
        ]
    },
    "cybersecurity": {
        "title": "Cybersecurity & Ethical Hacking",
        "category": "Security Engineering",
        "description": "Protection of computer systems and networks from information disclosure or theft.",
        "roadmap": ["Networking Fundamentals (TCP/IP, HTTP/S, DNS)", "Linux Security", "OWASP Top 10 Web Vulnerabilities", "Ethical Hacking & Penetration Testing", "Cryptography & PKI", "Security Information & Event Management (SIEM)"],
        "popular_frameworks": ["Wireshark", "Metasploit", "Nmap", "Burp Suite", "Kali Linux"],
        "project_ideas": ["Vulnerability Scanner", "Network Packet Sniffer", "Secure Auth API Implementation"],
        "interview_questions": [
            "What is OWASP Top 10?",
            "Difference between Symmetric and Asymmetric Encryption?",
            "What is SQL Injection and how do you prevent it?"
        ]
    }
}


def get_skill_knowledge(query_text):
    """
    Search the Skill Knowledge Base for relevant context to inject into AI prompts.
    """
    query_lower = query_text.lower()
    matched_skills = []

    for key, data in SKILL_KNOWLEDGE_BASE.items():
        if key in query_lower or any(kw in query_lower for kw in [data['title'].lower(), data['category'].lower()]):
            matched_skills.append(data)

    if not matched_skills:
        # Return generic list of available skills if no exact match
        return (
            "Available Skills in Skill Bank:\n"
            "- Python & Django Web Development\n"
            "- JavaScript, React.js & Frontend Systems\n"
            "- HTML5, CSS3 & Glassmorphic UI Design\n"
            "- SQL & Relational Databases (PostgreSQL/SQLite)\n"
            "- Machine Learning, AI & Data Science\n"
            "- DevOps, Docker, Cloud & Git Version Control\n"
            "- Cybersecurity & Ethical Hacking\n"
        )

    output = []
    for skill in matched_skills:
        output.append(f"### {skill['title']} ({skill['category']})")
        output.append(f"Overview: {skill['description']}")
        output.append(f"Learning Roadmap: {' -> '.join(skill['roadmap'])}")
        output.append(f"Frameworks/Tools: {', '.join(skill['popular_frameworks'])}")
        output.append(f"Project Ideas: {', '.join(skill['project_ideas'])}")
        output.append(f"Sample Interview Questions: {'; '.join(skill['interview_questions'])}\n")

    return "\n".join(output)
