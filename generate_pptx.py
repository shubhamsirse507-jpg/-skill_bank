import sys
import subprocess

# Ensure python-pptx is installed
try:
    import pptx
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    import pptx

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    PRIMARY_COLOR = RGBColor(14, 125, 115)   # #0e7d73 Teal
    DARK_BLUE = RGBColor(30, 58, 138)      # #1E3A8A Dark Navy
    TEXT_DARK = RGBColor(30, 41, 59)        # Slate Dark
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BG = RGBColor(241, 245, 249)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="SKILLBANK PLATFORM PRESENTATION"):
        # Header banner
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        shape.fill.solid()
        shape.fill.fore_color.rgb = PRIMARY_COLOR
        shape.line.fill.background()

        tf = shape.text_frame
        tf.margin_left = Inches(0.6)
        tf.margin_top = Inches(0.15)
        
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = RGBColor(153, 246, 228)

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = WHITE

    # SLIDE 1: Title Slide
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_BLUE
    bg1.line.fill.background()

    tf1 = bg1.text_frame
    tf1.margin_left = Inches(1.0)
    tf1.margin_top = Inches(2.2)

    p1 = tf1.paragraphs[0]
    p1.text = "SkillBank — Trade Skills, Not Money"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    p2 = tf1.add_paragraph()
    p2.text = "A Next-Generation Decentralized Skill Bartering, Live Learning & Verifiable Certification Platform"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(147, 197, 253)
    p2.space_before = Pt(15)

    p3 = tf1.add_paragraph()
    p3.text = "Full-Stack Web Architecture | Django & REST API | Academic & Industry Project 2026"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(226, 232, 240)
    p3.space_before = Pt(40)

    # SLIDE 2: Problem Statement
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Problem Statement: The Gap in Traditional Learning")
    
    tb2 = slide2.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    problems = [
        ("💰 High Cost of Quality Education", "Premium online courses and 1-on-1 tutoring carry heavy financial barriers for students and learners."),
        ("⌛ One-Way Passive Learning", "Traditional platforms rely on pre-recorded videos with zero real-time interaction, low completion rates, and delayed doubt resolution."),
        ("🔄 Underutilized Individual Expertise", "Students possess valuable skills (coding, design, languages, music) but lack a direct platform to trade skills without money."),
        ("📜 Lack of Verifiable Credentials", "Informal peer-learning models lack tamper-proof, publicly verifiable completion certificates.")
    ]

    for title, desc in problems:
        p = tf2.add_paragraph()
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE
        p.space_before = Pt(14)

        p_sub = tf2.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(14)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_before = Pt(2)

    # SLIDE 3: Project Objectives
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Project Objectives & Key Platform Innovations")

    tb3 = slide3.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    objectives = [
        ("🤝 Peer-to-Peer Skill Bartering System", "Enable users to offer their expertise in exchange for learning new skills without financial friction."),
        ("⚡ Instant Live Doubt Solving & Group Batches", "Real-time 15-minute doubt calls (90% mentor / 10% admin split) and multi-student scheduled batch courses."),
        ("💳 SkillBank Virtual Wallet", "Unified virtual credit system (₹250 initial signup bonus) to handle seamless skill credits and transactions."),
        ("📜 Verifiable Skill Completion Certificates", "Teacher-issued certificates backed by 128-bit UUID verification IDs for authentic achievement verification."),
        ("🛡️ Comprehensive Admin Control", "Centralized administration, teacher hiring approvals, content moderation, and immutable audit logs.")
    ]

    for title, desc in objectives:
        p = tf3.add_paragraph()
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_COLOR
        p.space_before = Pt(12)

        p_sub = tf3.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_before = Pt(2)

    # SLIDE 4: Backend Module Distribution
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Backend Module Distribution (Team Squad 1)")

    rows, cols = 5, 3
    table_shape4 = slide4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.2))
    table4 = table_shape4.table
    table4.columns[0].width = Inches(2.2)
    table4.columns[1].width = Inches(4.5)
    table4.columns[2].width = Inches(5.033)

    headers4 = ["Backend Member", "Designated Modules", "Core Responsibilities"]
    for i, h in enumerate(headers4):
        cell = table4.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.font.size = Pt(14)

    be_data = [
        ("Umair (Member 1)", "1. Authentication & Authorization Module\n2. User Management Module", "JWT Auth (SimpleJWT), OTP Email Verification, Password Reset, User Profiles, Role-Based Access Control."),
        ("Samarth (Member 2)", "1. Skill Management Module\n2. Course Management Module\n3. Learning Management Module", "Skill & Category CRUD, Search/Filter Engine, Group Batch Creation, Seat Limit Controls, Cataloging."),
        ("Savedita (Member 3)", "1. Live Doubt Solving Module\n2. Booking & Session Management\n3. Notification Management", "15-min Doubt Call Engine, 1-on-1 Session Scheduling, WebRTC/Jitsi Integration, Notification Alerts."),
        ("Neha (Member 4)", "1. Payment & Transaction Module\n2. Earnings & Commission Module\n3. Feedback & Rating Module", "Wallet Credits/Debits, Payment Receipts, 90/10 Fee Split Engine, Multi-Factor Ratings & Reviews (1-5 Stars).")
    ]

    for row_idx, row_data in enumerate(be_data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table4.cell(row_idx, col_idx)
            cell.text = text
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = TEXT_DARK

    # SLIDE 5: Frontend Module Distribution
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Frontend Module Distribution (Team Squad 2)")

    table_shape5 = slide5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.2))
    table5 = table_shape5.table
    table5.columns[0].width = Inches(2.2)
    table5.columns[1].width = Inches(4.5)
    table5.columns[2].width = Inches(5.033)

    headers5 = ["Frontend Member", "Designated Modules", "Core UI Components"]
    for i, h in enumerate(headers5):
        cell = table5.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY_COLOR
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.font.size = Pt(14)

    fe_data = [
        ("Shubham", "1. Authentication UI\n2. Profile Management UI\n3. Notification UI", "Responsive Login/Register/OTP pages, User Profile Customization, Notification Alerts & Top Navigation Bar."),
        ("Purva", "1. User Dashboard\n2. Skill Listing UI\n3. Responsive Layout", "Central User Dashboard (/user/), Skill Posting Cards, App Layout Framework, Mobile Sidebar & Theme System."),
        ("Priyanka", "1. Search & Filter UI\n2. Exchange Request UI\n3. Booking & Schedule UI", "Interactive Browse/Search Interface (/browse/), Exchange Request Modals, Booking Calendar & Schedules."),
        ("Dyani", "1. Messaging UI\n2. Review & Rating UI\n3. Admin Panel UI", "Direct Chat Messaging UI with Attachments, Review/Rating Submission Forms, Admin Dashboard (/admin-panel/).")
    ]

    for row_idx, row_data in enumerate(fe_data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table5.cell(row_idx, col_idx)
            cell.text = text
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = TEXT_DARK

    # SLIDE 6: Student Workflow
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Project Workflow: Student Journey (Top-to-Bottom)")

    tb6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.6))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    s_flow = [
        "1. REGISTRATION & ONBOARDING  ➜  Sign up via OTP/Email -> Setup Profile -> Receive ₹250 Initial Skill Credits.",
        "2. DISCOVERY & SEARCH       ➜  Filter categories (Web Dev, Languages, Design) -> Search offered skills.",
        "3. REQUEST & BOOKING        ➜  Send 1-on-1 Exchange Request OR Enroll in Group Batch OR Launch Doubt Call.",
        "4. WALLET PAYMENT           ➜  Deduct credits/balance -> Generate Automated Payment Receipt (UUID Invoice).",
        "5. LIVE LEARNING & CHAT     ➜  Attend Jitsi/WebRTC Video Session -> Direct Messaging with Instructor.",
        "6. CERTIFICATE & RATING     ➜  Receive Verifiable Skill Certificate -> Submit 1-5 Star Review & Ratings."
    ]

    for item in s_flow:
        p = tf6.add_paragraph()
        p.text = item
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE
        p.space_before = Pt(14)

    # SLIDE 7: Teacher Workflow
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Project Workflow: Teacher Journey (Top-to-Bottom)")

    tb7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.6))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    t_flow = [
        "1. HIRING & VERIFICATION    ➜  Submit Teacher Application & Resume -> Admin Approves Hiring Status.",
        "2. CONTENT LISTING          ➜  Post Offered Skill Listings -> Create Multi-Student Group Batches (Seats & Credits).",
        "3. REQUEST MANAGEMENT       ➜  Review incoming requests -> Accept, reschedule, or chat with students.",
        "4. LIVE CLASS EXECUTION     ➜  Host interactive video sessions -> Guide learners -> Mark session Completed.",
        "5. EARNINGS & CERTIFICATES  ➜  Earn Wallet Credits (90% Doubt Split / Batch Fees) -> Issue Verifiable Certificate."
    ]

    for item in t_flow:
        p = tf7.add_paragraph()
        p.text = item
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_COLOR
        p.space_before = Pt(18)

    # SLIDE 8: Admin Workflow
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Project Workflow: Admin Journey (Top-to-Bottom)")

    tb8 = slide8.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.6))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    a_flow = [
        "1. PLATFORM OVERVIEW       ➜  Monitor total active users, ongoing sessions, system health, and receipts.",
        "2. USER & HIRING CONTROL    ➜  Review pending teacher applications -> Grant staff/teacher role -> Suspend accounts.",
        "3. CONTENT MODERATION       ➜  Manage skill categories -> Approve/delete skill listings -> Review user reports.",
        "4. AUDIT LOGS & NOTICES     ➜  Inspect immutable System Audit Logs -> Broadcast global platform announcements."
    ]

    for item in a_flow:
        p = tf8.add_paragraph()
        p.text = item
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE
        p.space_before = Pt(22)

    # SLIDE 9: DB Info Part 1
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Database Architecture & Specs (DB Info — Part 1)")

    tb9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.5))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    db1_items = [
        ("🗄️ Dual-Database Engine Strategy", "Development uses SQLite 3 (db.sqlite3) for fast local prototyping. Production uses Enterprise PostgreSQL via dj-database-url with SSL connection pooling."),
        ("⚡ Object-Relational Mapping (Django ORM)", "All data interactions use Django ORM parametrized queries, guaranteeing security against SQL Injection attacks."),
        ("🔐 UUID Identifiers & Security", "Uses 128-bit Universally Unique Identifiers (UUID) for SkillCertificate and PaymentReceipt to prevent URL manipulation."),
        ("🛡️ Constraints & Indexing", "Enforces unique_together constraints on BatchEnrollment to prevent double booking. Indexes high-frequency fields (scheduled_date, created_at, status).")
    ]

    for title, desc in db1_items:
        p = tf9.add_paragraph()
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_COLOR
        p.space_before = Pt(14)

        p_sub = tf9.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_before = Pt(2)

    # SLIDE 10: DB Info Part 2
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Database Schema & 18-Model Relational Specs (DB Info — Part 2)")

    table_shape10 = slide10.shapes.add_table(7, 3, Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.5))
    table10 = table_shape10.table
    table10.columns[0].width = Inches(2.5)
    table10.columns[1].width = Inches(4.5)
    table10.columns[2].width = Inches(4.733)

    headers10 = ["Functional Layer", "Database Models", "Description & Relationships"]
    for i, h in enumerate(headers10):
        cell = table10.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.font.size = Pt(13)

    db_data = [
        ("Auth & Profile", "User, UserProfile, OTPVerification", "Credentials, extended bio, headline, phone, role, 6-digit OTP tokens."),
        ("Skill & Certificate", "SkillCategory, Skill, SkillCertificate", "Categories, offered/wanted skills, verifiable UUID certificates."),
        ("Messaging", "SkillExchange, Conversation, Message", "Exchange requests, 1-on-1 chat rooms, file attachments."),
        ("Bookings & Batches", "Booking, Batch, BatchEnrollment, DoubtCall", "1-on-1 sessions, group courses, seat limits, 15-min doubt calls."),
        ("Financial", "Wallet, WalletTransaction, PaymentReceipt, Payment", "Wallet balance (₹250 default), credit/debit logs, invoice receipts."),
        ("Governance & Ratings", "ReviewRating, TeacherHiring, PlatformReport, AuditLog", "1-5 star reviews, teacher hiring queue, user reports, audit log.")
    ]

    for row_idx, row_data in enumerate(db_data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table10.cell(row_idx, col_idx)
            cell.text = text
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_DARK

    # SLIDE 11: Security & Deployment
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Security Architecture & Cloud Deployment Pipeline")

    tb11 = slide11.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.5))
    tf11 = tb11.text_frame
    tf11.word_wrap = True

    sec_items = [
        ("🔐 JWT Authentication & Password Security", "rest_framework_simplejwt with refresh token rotation & token blacklisting. Django password hashing with PBKDF2."),
        ("🛡️ CSRF & CORS Security", "CsrfViewMiddleware enforces CSRF tokens. django-cors-headers restricts unauthorized cross-origin requests."),
        ("🚀 Cloud Deployment Pipeline", "WSGI Server Gunicorn (Procfile). WhiteNoise serves static assets efficiently. Render/Railway automated deployments via build.sh."),
        ("🔒 Environment Variable Isolation", "python-dotenv isolates sensitive keys (SECRET_KEY, EMAIL_HOST_PASSWORD, DATABASE_URL) from git repositories.")
    ]

    for title, desc in sec_items:
        p = tf11.add_paragraph()
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = DARK_BLUE
        p.space_before = Pt(14)

        p_sub = tf11.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_before = Pt(2)

    # SLIDE 12: Conclusion & Future Roadmap
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Conclusion & Future Roadmap")

    tb12 = slide12.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.5))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    conc_items = [
        ("🎉 Project Summary", "Successfully designed and built SkillBank — a full-stack peer-to-peer skill bartering platform featuring live video calls, group batches, virtual wallets, and verifiable certificates."),
        ("👥 Modular Team Execution", "Divided into 8 specialized modules across Backend (Umair, Samarth, Savedita, Neha) and Frontend (Shubham, Purva, Priyanka, Dyani) squads."),
        ("📱 Native Mobile Application", "Develop React Native / Flutter mobile app using existing REST API v1 endpoints."),
        ("🧠 AI Skill Matching Engine", "Implement intelligent machine learning matching algorithm for personalized skill recommendations."),
        ("🌐 Blockchain Credentialing", "Migrate skill certificates to decentralized blockchain smart contracts for immutable global verification.")
    ]

    for title, desc in conc_items:
        p = tf12.add_paragraph()
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_COLOR
        p.space_before = Pt(12)

        p_sub = tf12.add_paragraph()
        p_sub.text = desc
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_DARK
        p_sub.space_before = Pt(2)

    out_file = "SkillBank_Presentation.pptx"
    prs.save(out_file)
    print(f"✅ Successfully generated presentation file: {out_file}")

if __name__ == "__main__":
    build_presentation()
