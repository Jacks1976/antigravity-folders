# 🚀 Quick Start Guide - PIBG Application

## Step 1: Start Backend (Terminal 1)
```bash
cd "c:\Users\dieke\Documents\Antigravity folders"
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## Step 2: Start Frontend (Terminal 2)
```bash
cd "c:\Users\dieke\Documents\Antigravity folders\web"
npm run dev
```

Expected output:
```
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Environments: .env.local
```

## Step 3: Open Application
```
http://localhost:3000
```

You'll be redirected to login page.

---

## Test Accounts

### Admin Account
- **Email:** admin@pibg.church
- **Password:** Admin123!@#
- **Role:** Admin
- **Access:** All pages + admin panels

### Staff Account
- **Email:** staff@pibg.church
- **Password:** Staff123!@#
- **Role:** Staff
- **Access:** Events, announcements, member directory

### Member Account
- **Email:** membro1@pibg.church
- **Password:** Member123!@#
- **Role:** Member
- **Access:** Public pages, event RSVP

### Pending Member Account
- **Email:** visitante1@pibg.church
- **Password:** Visitor123!@#
- **Role:** Pending
- **Access:** Limited (pending approval)

---

## What to Test

### 1. Login Form Validation (/login)
- Try empty email → Error message appears
- Try invalid email (abc@) → Red border + error
- Try short password → Error toast appears
- Login with correct credentials → Success toast + redirects to /dashboard

### 2. Register Form (/register)
- Try password shorter than 12 chars → Shows "Mínimo de 12 caracteres"
- Try password without uppercase → Shows "Precisa de letras maiúsculas"
- Try password without numbers → Shows "Precisa de números"
- Try password without symbols → Shows "Precisa de símbolos (!@#$%^&*)"
- Try mismatched passwords → Shows "As senhas não correspondem"
- Complete registration → Success toast

### 3. Dashboard (/dashboard) [Logged in as Admin]
- Should show welcome message with real name (Pastor João Silva)
- Shows event count (13 events)
- Shows member count (10 members)
- Shows announcements count

### 4. Events Page (/events)
- Lists 13 church events (Culto Matutino, Ensaio, etc.)
- Each event shows title, date, time
- Click event to see details
- Admin can create new event with toast feedback

### 5. Announcements (/announcements)
- Shows 14 announcements
- Each with date, title, body
- Admin can post new announcement with toast notification

### 6. Members (/members)
- Shows list of 10 members with names
- Member profiles from database

### 7. Worship Management (/worship/repertoire, /worship/schedule)
- Repertoire shows 10 worship songs
- Songs have title, artist, BPM, key

### 8. Admin Panels (/admin/events, /admin/announcements, /admin/members, /admin/users)
- Create event → Success toast "Evento criado com sucesso!"
- Create announcement → Success toast "Anúncio criado com sucesso!"
- Error handling with error toasts

---

## Key Features to Notice

### 🎨 Toast Notifications
- Bottom-right notifications
- Green for success
- Red for errors
- Blue for info
- Yellow for warnings
- Auto-dismiss after 5 seconds

### 📝 Form Validation
- Real-time error messages
- Red input borders on error
- Field-level error hints
- Disabled buttons during API calls

### 📊 Real Test Data
- Church-specific names (Pastor João Silva, Diaconisa Maria Santos)
- Church events (Culto Matutino, Ensaio, Reunião)
- Brazilian worship songs (Grande é o Senhor, Magnificência, etc.)
- Realistic timestamps (past, current, future events)

### 🔒 Authentication
- JWT tokens stored in localStorage
- Auto-logout after session expires
- Role-based page access
- Protected admin pages

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
# Kill process or change port:
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -r .next node_modules
npm install
npm run dev
```

### Database issues
```bash
# Reset database with fresh seed data
python execution/setup_database.py
python execution/seed_pibg_data.py
```

### Login always fails
```bash
# Check if backend is running on port 8000
# Check database has seed data:
python
>>> import sqlite3
>>> conn = sqlite3.connect('church_app.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT COUNT(*) FROM users")
>>> print(cursor.fetchone())  # Should show 15+ users
```

---

## File Locations

```
Project Root: c:\Users\dieke\Documents\Antigravity folders\

Backend Files:
  ├── app/main.py (FastAPI app)
  ├── app/routers/ (API endpoints)
  ├── app/schemas/ (Request/response models)
  ├── app/services/ (Business logic)
  ├── app/core/ (Auth, dependencies)
  └── execution/ (Database setup, seed)

Frontend Files:
  ├── web/app/ (Next.js pages)
  ├── web/app/layout.tsx (Root layout with providers)
  ├── web/components/ (React components)
  ├── web/lib/ (Utilities, hooks, context)
  └── web/public/ (Static assets)

Database:
  └── church_app.db (SQLite file at project root)

Configuration:
  ├── .env.local (Frontend env vars)
  ├── web/tsconfig.json (TypeScript config)
  ├── web/next.config.js (Next.js config)
  └── web/tailwind.config.js (Tailwind CSS)
```

---

## Common Tasks

### Add new test user
```bash
# Edit execution/seed_pibg_data.py, add to users list, then:
python execution/seed_pibg_data.py
```

### Create new admin form
```bash
# 1. Create page component in web/app/admin/[feature]/page.tsx
# 2. Import useToast: const { success, error } = useToast()
# 3. Wrap API calls in try/catch with success/error toasts
# 4. Add validation using validators.ts
```

### Add new API route
```bash
# 1. Create router in app/routers/[feature].py
# 2. Add to app/main.py: app.include_router([feature].router)
# 3. Add schema in app/schemas/[feature].py
# 4. Add apiClient method in web/lib/api-client.ts
# 5. Use in frontend components
```

### View database
```bash
# Using SQLite CLI
sqlite3 church_app.db

# Common queries:
> SELECT COUNT(*) FROM users;
> SELECT email, role, status FROM users WHERE deleted_at IS NULL;
> SELECT COUNT(*) FROM events;
> SELECT title FROM announcements LIMIT 5;
```

---

## Next Development Phase

Priority improvements:
1. Loading spinners on buttons
2. Error boundary for crashes
3. Real-time email duplicate check
4. Success animation on submit
5. Messaging system
6. Prayer request feature

See `PHASE1_COMPLETE.md` for full roadmap.

---

## Support Commands

```bash
# Type check frontend
cd web && npm run type-check

# Lint frontend code
cd web && npm run lint

# Format frontend code
cd web && npm run format

# Check backend code
cd app && python -m flake8 .

# Run backend tests (if implemented)
cd app && python -m pytest

# View realtime logs (backend)
# Keep backend terminal open to see logs

# View realtime logs (frontend)
# Keep frontend terminal open to see build output
```

---

## Architecture Overview

```
User Browser (localhost:3000)
    ↓ HTTPS
Next.js Frontend (React 18, Tailwind CSS)
    ├── Toast System (bottom-right notifications)
    ├── Auth Context (JWT, user state)
    ├── Validation (client-side form checks)
    └── API Client (calls backend)
    ↓ JSON REST API
FastAPI Backend (localhost:8000)
    ├── Auth Router (login, register, JWT)
    ├── Members Router (profiles, directory)
    ├── Events Router (CRUD events)
    ├── Announcements Router (feed, create)
    ├── Worship Routers (songs, schedules, files)
    └── Admin Routers (user management)
    ↓ SQL Queries
SQLite Database (church_app.db)
    ├── users (10 test accounts)
    ├── member_profiles (names and bios)
    ├── events (13 church events)
    ├── announcements (14 posts)
    ├── songs (10 worship songs)
    └── Other tables
```

---

**Last Updated:** Phase 1 Complete
**Status:** Ready for Testing
**Build:** ✅ Production Build Successful
