# 🎓 SkillBank — Peer-to-Peer Skill Exchange & Learning Platform

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15-red.svg?style=flat&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![JWT Auth](https://img.shields.io/badge/Auth-SimpleJWT-black.svg?style=flat&logo=json-web-tokens&logoColor=white)](https://jwt.io/)
[![Database](https://img.shields.io/badge/Database-SQLite3-4169E1.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Deployment](https://img.shields.io/badge/Deployment-Render%20%7C%20Railway-46E3B7.svg?style=flat&logo=render&logoColor=white)](https://render.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**SkillBank** is a comprehensive, production-ready full-stack Django platform designed to facilitate peer-to-peer skill exchanges, structured batch courses, live 1-on-1 mentorship, and doubt-clearing sessions. Whether trading Python programming lessons for Graphic Design guidance or booking structured masterclasses, SkillBank connects mentors and learners around the globe.

---

## 🌟 Key Features

### 🔐 1. Authentication & User Management (`authentication`)
- **Multi-Method Login**: Username/Email login with JWT bearer tokens for REST clients and session cookies for web UI.
- **OTP Verification**: Email/SMS OTP generation and verification for secure account activation.
- **Password Reset Flow**: Secure token-based password reset mechanism.

### 👤 2. Profiles & Reputation System (`profiles`, `ratings`)
- **Rich User Profiles**: Customizable avatars, headlines, bio, social links, and role designations (Learner, Teacher, Admin).
- **Skill Portfolios**: Dedicated lists for skills offered and skills wanted.
- **Ratings & Reviews**: Peer rating system with 5-star scoring, detailed feedback, and badge awards.

### 🎯 3. Skill Management & Discovery (`skill_management`, `search`)
- **Categorized Taxonomy**: Hierarchical categories (e.g., Software Development, Graphic Design, Languages, Music).
- **Advanced Search & Filtering**: Multi-parameter search by category, difficulty level, popularity, ratings, and keyword filters.

### 📅 4. Bookings, Batches & Live Sessions (`bookings`)
- **1-on-1 Mentorship Bookings**: Schedule individual mentorship sessions with real-time status tracking (Pending, Confirmed, Completed, Cancelled).
- **Batch Courses**: Enroll in multi-student structured learning cohorts.
- **Doubt Clearing**: Dedicated short-format sessions for instant query resolution.

### 💬 5. Real-Time Messaging & Exchange Proposals (`messaging`)
- **Direct Messaging**: Direct user-to-user conversation threads.
- **Exchange Proposals**: Propose skill swaps with session duration, agreed terms, and interactive accept/decline workflows.

### 💳 6. Wallet & Payments (`payments`)
- **SkillBank Virtual Wallet**: Track token/coin balances or virtual credits used to book sessions.
- **Transaction History & Receipts**: Itemized audit logs and downloadable payment receipts for every transaction.

### 🤖 7. AI Chat Assistant ("Chatboat") (`chatboat`)
- **Intelligent Guidance**: Integrated AI assistant recommending courses, suggesting skill pairings, and answering platform FAQs.

### 🛡️ 8. Administration & Moderation (`admin_panel`)
- **Platform Analytics**: Audit logs, system health reports, and platform broadcast notices.
- **Moderation Tools**: Review user activity, handle platform reports, and manage system announcements.

### 📚 9. Interactive API Documentation (`api`)
- **OpenAPI / Swagger UI**: Test REST endpoints interactively at `/api/v1/docs/`.
- **ReDoc**: Clean, responsive API reference documentation at `/api/v1/redoc/`.

---

## 🛠️ Tech Stack & Architecture

- **Backend Framework**: Python 3.11, Django 4.2+
- **API Engine**: Django REST Framework (DRF), `drf-yasg` (Swagger/OpenAPI 2.0)
- **Authentication**: JWT (`djangorestframework-simplejwt`), Session Authentication
- **Frontend Architecture**: HTML5, Custom Responsive Vanilla CSS Design System, Django Templates, JavaScript
- **Database**: SQLite3 (`db.sqlite3`) saved in project root
- **WSGI & Static Asset Server**: Gunicorn 22.0, WhiteNoise 6.7
- **Deployment Targets**: Render.com Blueprint (`render.yaml`), Railway.app, PythonAnywhere

---

## 📁 Project Directory Structure

```text
skill_bank/
├── admin_panel/            # Platform audit logs, notices, health reports
├── api/                    # Centralized REST API v1 routing & serializers
├── authentication/         # User auth, OTP verification, password reset
├── bookings/               # Session bookings, batch courses, doubt sessions
├── chatboat/               # AI Chatbot assistant service
├── dashboard/              # Main landing & platform dashboard views
├── messaging/              # Conversations, messages, & skill exchange offers
├── notifications/          # User notification system
├── payments/               # Wallet management, transactions, & receipts
├── profiles/               # UserProfile models & management
├── ratings/                # Peer reviews, 5-star ratings, & metrics
├── search/                 # Search & discovery service
├── skill_bank/             # Core project configuration (settings.py, urls.py, wsgi.py)
├── skill_management/       # Skills & Skill Categories models & views
├── user_dashboard/         # Student & Mentor personalized dashboard views
├── templates/              # HTML layout templates & component views
├── static/                 # Static CSS, JS, and image assets
├── media/                  # User uploads (avatars, attachments)
├── build.sh                # Production build script (migrate, collectstatic)
├── DEPLOYMENT_GUIDE.md     # Production deployment instructions
├── Procfile                # Gunicorn process launch file
├── render.yaml             # Render 1-click blueprint deployment file
├── requirements.txt        # Python package dependencies
├── runtime.txt             # Python engine specification (3.11.8)
└── manage.py               # Django management CLI script
```

---

## 🚀 Quick Start & Local Setup

### Prerequisites
- **Python 3.11+** installed
- **Git** installed

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/skill_bank.git
cd skill_bank
```

### 2. Create and Activate a Virtual Environment
- **On Windows (PowerShell / CMD)**:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **On macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (or copy from `.env.example`):
```bash
cp .env.example .env
```

Example `.env` configuration:
```env
SECRET_KEY=django-insecure-your-custom-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Database Engine (SQLite3 saved in root as db.sqlite3)
DB_NAME=db.sqlite3
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser & Seed Demo Accounts
- **Create Admin Superuser**:
  ```bash
  python manage.py createsuperuser
  ```
- **Seed Pre-populated Demo Users & Sample Data**:
  ```bash
  python create_demo_users.py
  ```
  *Default Demo Accounts:*
  - **Regular User**: `demouser` / `DemoPassword123!`
  - **Teacher User**: `demoteacher` / `TeacherPassword123!`

### 7. Run Local Development Server
```bash
python manage.py runserver
```
Visit the application in your web browser at:
- **Web UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin**: [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)
- **Swagger API Docs**: [http://127.0.0.1:8000/api/v1/docs/](http://127.0.0.1:8000/api/v1/docs/)
- **ReDoc API Docs**: [http://127.0.0.1:8000/api/v1/redoc/](http://127.0.0.1:8000/api/v1/redoc/)

---

## 🌐 Main Application Routes & API Endpoints

### Core Web UI Pages
| Route | View Description |
|---|---|
| `/` | Landing page / Authentication Portal |
| `/dashboard/` | Main platform overview dashboard |
| `/user/` | Personalized User Dashboard |
| `/profile/` | Manage User Profile, Skills Offered/Wanted |
| `/browse/` | Search & Filter Skills |
| `/bookings/` | My Session Bookings & Schedule |
| `/batches/` | Enrolled Batch Courses |
| `/live/` | Live Sessions Lobby |
| `/doubt/` | Doubt Clearing Forum |
| `/messaging/` | Direct Inbox & Exchange Proposals |
| `/wallet/` | SkillBank Wallet & Balance |
| `/receipts/` | Transaction Receipts |
| `/chat/` | AI Assistant Chat Interface |
| `/admin-panel/` | Admin Control Center & Audit Logs |

### REST API Endpoints (`/api/v1/`)
| Endpoint | HTTP Method | Description |
|---|---|---|
| `/api/v1/auth/login/` | `POST` | Obtain JWT Access & Refresh Tokens |
| `/api/v1/auth/token/refresh/` | `POST` | Refresh JWT Access Token |
| `/api/v1/auth/register/` | `POST` | Register a new user account |
| `/api/v1/profiles/` | `GET`, `PUT` | Manage current user profile |
| `/api/v1/skills/` | `GET`, `POST` | List and create available skills |
| `/api/v1/bookings/` | `GET`, `POST` | Retrieve bookings or create new session booking |
| `/api/v1/payments/wallet/` | `GET` | Retrieve wallet balance & transaction history |
| `/api/v1/docs/` | `GET` | Interactive Swagger API Explorer |

---

## 🚢 Deployment Guide

SkillBank is pre-configured for automated 1-click cloud deployment.

### Option 1: Render.com (Recommended)
1. Push your repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Blueprint**.
3. Select your GitHub repository. Render automatically reads `render.yaml`, executes `build.sh` (installs packages, runs migrations, collects static files), and starts Gunicorn.

### Option 2: Railway.app
1. Connect your repository on [Railway.app](https://railway.app/).
2. Define environment variables (`SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`).
3. Railway automatically detects `Procfile` and deploys the WSGI server.

---

## 📤 Pushing to GitHub Main Branch

To add and push the `README.md` file (and any recent updates) to your `main` branch on GitHub:

```bash
# 1. Stage the README.md file
git add README.md

# 2. Commit the changes
git commit -m "docs: add comprehensive project README file"

# 3. Push to GitHub main branch
git push origin main
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
