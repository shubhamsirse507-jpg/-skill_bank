# Skill Bank

A Django-based skill exchange platform featuring a modern dark glassmorphism UI.

## Apps

- **messaging** — Conversation UI for accepted/requested skill exchanges
- **ratings** — Review & Rating Hub for completed sessions

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install django

# Apply migrations
python manage.py migrate

# Seed demo data (Dnyani, Umair, Shubham)
python manage.py seed_data

# Run server
python manage.py runserver
```

## URLs

- Messaging UI: `http://127.0.0.1:8000/messages/`
- Rating & Review UI: `http://127.0.0.1:8000/ratings/`
