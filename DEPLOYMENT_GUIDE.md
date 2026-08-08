# 🚀 SkillBank Deployment Guide

This guide walks you through deploying the **SkillBank Platform** to production. All production configuration files (`Procfile`, `requirements.txt`, `build.sh`, `render.yaml`, `runtime.txt`) have been prepared for you.

---

## 🛠 Prepared Production Files

| File | Purpose |
|---|---|
| [requirements.txt](file:///d:/Django_framework/skill_bank/requirements.txt) | Includes Gunicorn, WhiteNoise, PostgreSQL driver (`psycopg2-binary`), and `dj-database-url`. |
| [Procfile](file:///d:/Django_framework/skill_bank/Procfile) | Defines web process command: `web: gunicorn skill_bank.wsgi:application`. |
| [build.sh](file:///d:/Django_framework/skill_bank/build.sh) | Automated build script that installs dependencies, collects static files, and applies migrations. |
| [render.yaml](file:///d:/Django_framework/skill_bank/render.yaml) | Render Blueprint configuration for 1-click automated deployment. |
| [runtime.txt](file:///d:/Django_framework/skill_bank/runtime.txt) | Specifies Python version `python-3.11.8`. |

---

## Option 1: Render.com Deployment (Recommended — Free & Easy)

Render provides free hosting with HTTPS certificates, static file serving (via WhiteNoise), and optional PostgreSQL database.

### Step 1: Push Code to GitHub
1. In your local terminal, initialize git (if not done) and commit all changes:
   ```bash
   git add .
   git commit -m "SkillBank production release ready"
   git push origin main
   ```

### Step 2: Create Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Blueprint**.
2. Connect your GitHub repository containing `SkillBank`.
3. Render will automatically detect `render.yaml` and configure the service.
4. Click **Apply**. Render will automatically run `build.sh`, collect static files, apply migrations, and launch your site!

### Step 3: Access Your Live Site
Your app will be live at a URL like: `https://skillbank-platform.onrender.com`

---

## Option 2: Railway.app Deployment

1. Go to [Railway.app](https://railway.app/) and click **New Project** -> **Deploy from GitHub repo**.
2. Select your `SkillBank` repository.
3. In **Variables**, add:
   - `SECRET_KEY`: `your-secure-random-secret-key`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*`
4. Railway will automatically detect Gunicorn from `Procfile` and deploy your app.

---

## Option 3: PythonAnywhere Deployment

1. Open bash console on [PythonAnywhere](https://www.pythonanywhere.com/).
2. Clone repository:
   ```bash
   git clone <your-repo-url> skill_bank
   cd skill_bank
   mkvirtualenv --python=/usr/bin/python3.11 skillbank-env
   pip install -r requirements.txt
   python manage.py collectstatic --no-input
   python manage.py migrate
   ```
3. In **Web** tab:
   - Set **Source Code**: `/home/<username>/skill_bank`
   - Set **Virtualenv**: `/home/<username>/.virtualenvs/skillbank-env`
   - Set **WSGI file**: point to `/home/<username>/skill_bank/skill_bank/wsgi.py`
4. Click **Reload**.

---

## 🔒 Recommended Production Environment Variables

In your hosting provider's Environment Variables settings:

```env
SECRET_KEY=generate-a-strong-random-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com,.railway.app,yourcustomdomain.com
DATABASE_URL=postgres://username:password@ep-host.region.aws.neon.tech/neondb
```

*(Note: If `DATABASE_URL` is omitted, the app safely defaults to SQLite `db.sqlite3`.)*
