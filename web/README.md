# Church Agenda Web UI

Next.js web application for Church Agenda management system.

## Prerequisites

- Node.js 18+ and npm
- Running FastAPI backend (see `../execution` and `../app`)

## Installation

```bash
cd web
npm install
```

## Configuration

1. Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```

2. Update `.env.local` with your API base URL:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Running the Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Features

- **Authentication**: Login and registration with JWT tokens
- **Dashboard**: Overview of upcoming events and latest announcements
- **Events**: Browse events, RSVP (going/maybe/not going)
- **Announcements**: View targeted announcements with pagination
- **Members**: Directory with search and privacy controls
- **Worship Repertoire**: Manage song library with metadata (title, artist, BPM, key)
  - Add/edit songs
  - Upload MP3/PDF files or add YouTube/Drive links
  - Search and filter songs
- **Worship Schedule**: Create and manage service plans
  - Create service plans with dates and notes
  - Add songs to setlists
  - Assign musicians to roster
  - Confirm/decline roster assignments
- **Admin Panel** (Admin-only):
  - **User Management**: Approve pending users, view all users with status badges
  - **Ministry Management**: Assign members to ministries with roles and lead status
  - **Event Management**: Create events with visibility and ministry targeting
  - **Announcement Management**: Create targeted announcements (global/role/ministry)
- **i18n**: Multi-language support (pt-BR, en, es)

## Project Structure

```
web/
├── app/                    # Next.js App Router pages
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   ├── dashboard/         # Dashboard (authenticated)
│   ├── events/            # Events list with RSVP
│   ├── announcements/     # Announcements feed
│   ├── members/           # Members directory
│   ├── worship/           # Worship module
│   │   ├── repertoire/    # Song library management
│   │   └── schedule/      # Service plan scheduling
│   └── admin/             # Admin panel (admin-only)
│       ├── users/         # User approval and management
│       ├── members/       # Ministry assignment
│       ├── events/        # Event creation
│       └── announcements/ # Announcement creation
├── components/            # Reusable React components
│   └── Navigation.tsx     # Main navigation bar
├── lib/                   # Core libraries
│   ├── api-client.ts      # API client with typed methods
│   ├── auth-context.tsx   # Authentication context/hooks
│   └── i18n-context.tsx   # Internationalization context
└── messages/              # Translation files
    ├── pt-BR.json         # Portuguese (Brazil)
    ├── en.json            # English
    └── es.json            # Spanish
```

## API Integration

All API calls use the standard response envelope:
```json
{
  "ok": boolean,
  "data": any | null,
  "error_key": string | null
}
```

All endpoints return HTTP 200. Errors are indicated by `ok: false` and `error_key` containing a translation key.

## Translation Keys

The UI uses translation keys for all user-facing text. See `messages/*.json` for available keys.

Error keys from the API are automatically translated using the current locale.

## Language Switching

Use the language selector in the navigation bar to switch between:
- 🇧🇷 Portuguese (Brazil) - default
- 🇺🇸 English
- 🇪🇸 Spanish

Language preference is stored in localStorage.

## Building for Production

```bash
npm run build
npm start
```

## Notes

- JWT tokens are stored in localStorage (MVP approach)
- All timestamps from API are in UTC and displayed in user's locale
- Privacy controls respect API field-level permissions
- Pagination uses limit+offset pattern
