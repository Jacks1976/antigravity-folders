# Master Plan: Church Agenda Application

## Purpose
Defines the global architecture, roles, permissions, security standards, and internationalization rules for the Church Agenda application. All other directives inherit these standards.

## Roles & Permissions Matrix

| Resource | Action | Public | Pending | Active Member | Volunteer | Musician | Staff/Admin |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Members** | View Directory | - | - | Own Profile | Own Profile | Own Profile | Full Access |
| **Members** | Manage Status/Roles | - | - | - | - | - | Yes |
| **Events** | View | Public Only | Public Only | Public + Internal | Public + Internal | Public + Internal | All |
| **Events** | Create/Edit | - | - | - | - | - | Yes |
| **RSVPs** | Respond | Public Events | - | Yes | Yes | Yes | Yes |
| **Announcements** | View | - | - | Assigned | Assigned | Assigned | All |
| **Announcements** | Create/Pin | - | - | - | Ministry Lead | Ministry Lead | Yes |
| **Rehearsals** | View Schedule | - | - | - | - | Own | Manage |
| **Roster/Scale** | Manage | - | - | - | - | - | Worship Lead |
| **Audio Library** | Access/Download | - | - | - | - | Yes | Yes |
| **Audio Library** | Upload/Manage | - | - | - | - | - | Worship Lead |
| **Messaging** | Send DM | - | - | Yes | Yes | Yes | Yes |
| **Forum** | Read/Post | - | - | Yes | Yes | Yes | Moderate |
| **Admin Settings**| Manage System | - | - | - | - | - | Yes |

*Note: "Musician" and "Volunteer" imply "Active Member" base rights.*

## Global Data Standards

### Internationalization (i18n)
- **Supported Languages**: Portuguese (`pt-BR`), English (`en`), Spanish (`es`).
- **Configuration Hierarchy** (Fallback Order):
    1. **User Preference**: Explicitly set in profile.
    2. **Organization Default**: Set by Admin (default: `pt-BR`).
    3. **System Fallback**: `pt-BR`.
- **Formatting Rules**:
    - **UI Text**: All strings must use translation keys (e.g., `{{ t('auth.login') }}`).
    - **Dynamic Data**: User-generated content remains in original language.
    - **Dates/Numbers**: Format according to the *Viewer's* locale (e.g., `DD/MM/YYYY` for BR, `MM/DD/YYYY` for US).
    - **Timezones**: Store all timestamps in UTC. Display converting to User's local timezone.

### Security
1.  **Password Hashing**: Argon2id (params: m=65536, t=3, p=4).
2.  **Session Management**:
    - **Access Token**: Short-lived (15-30 min) JWT.
    - **Refresh Token**: Long-lived (7-30 days) HttpOnly, Secure, SameSite=Strict cookie.
    - **CSRF**: Anti-forgery tokens required for all state-changing methods (POST, PUT, DELETE, PATCH).
3.  **Audit Logging**:
    - **Format**: `timestamp` (UTC), `actor_id`, `action_type`, `resource_id`, `ip_address`, `user_agent`, `metadata`.
    - **Tracked Events**:
        - `AUTH_LOGIN_SUCCESS`, `AUTH_LOGIN_FAIL`, `AUTH_LOGOUT`
        - `MEMBER_CREATE`, `MEMBER_UPDATE`, `MEMBER_DELETE`, `ROLE_CHANGE`, `STATUS_CHANGE`
        - `AUDIO_UPLOAD`, `AUDIO_DOWNLOAD`, `AUDIO_DELETE`
        - `EVENT_PUBLISH`, `ANNOUNCEMENT_PUBLISH`
4.  **Transport**: HTTPS Mandatory (HSTS recommended).

## High-Level Architecture
- **Frontend**: Web Application (React/Next.js).
- **Backend**: API (Node.js/Python).
- **Database**: Relational DB (PostgreSQL).

## Execution (Placeholders)
- `execution/setup_database.py`
- `execution/seed_roles.py`
