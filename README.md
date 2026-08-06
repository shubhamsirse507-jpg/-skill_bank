# 🏦 SkillBank

SkillBank is a web application designed to manage student and teacher accounts, with secure authentication and role-based access. Built as a team project — backend in Django, frontend built and integrated via GitHub.

---

## 🚀 Features

- **User Authentication** — Registration, login, and forgot-password flows
- **OTP Email Verification** — Secure sign-up via Gmail SMTP-based one-time passwords
- **Role-Based Access Control** — Separate permissions and views for `student` and `teacher` roles
- **Secure Password Storage** — Passwords hashed using SHA-256
- **Modular Backend Architecture** — Clean separation of concerns across authentication, dashboard, and profile modules
- **Responsive Frontend UI** — Built with a modern component-based interface, integrated with the Django backend

---

## 🧰 Tech Stack

**Backend**
- Python
- Django
- SQLite (development) / MySQL (production-ready)
- SMTP (Gmail) for OTP email delivery

**Frontend**
- Built with a modern UI builder, integrated via GitHub
- HTML, CSS, JavaScript

**Tools**
- Git & GitHub for version control and collaboration
- VS Code

---

## 📂 Project Structure

```
skill_bank/
├── authentication/       # Registration, login, OTP, password reset
├── dashboard/             # Role-based dashboard views
├── profiles/               # User profile management
├── media/                   # Uploaded media (profile photos, etc.)
├── itr_project/            # Project settings and configuration
├── manage.py
├── requirements.txt
└── db.sqlite3
```

---

## ⚙️ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shubhamsirse507-jpg/-skill_bank.git
   cd -skill_bank
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000/` in your browser.

---

## 👥 Team & Roles

- **Backend Development** — Authentication, authorization, database design, and role-based access control
- **Frontend Development** — UI design and integration

---

## 📌 Status

Actively in development — authentication and authorization modules complete; dashboard and profile features in progress.

---

## 📄 License

This project is for academic/educational purposes as part of a diploma engineering project.

