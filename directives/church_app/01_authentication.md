# Directive: Authentication Module

## Purpose
Manage user identity, secure login/logout, session handling, and registration lifecycle.

## Roles
- **Public**: Can Register/Login.
- **Pending Member**: Account created but not approved. **No internal access.**
- **Active Member (base)**: Approved account with standard access.
    - *Note*: **Volunteer**, **Musician**, and **Staff/Admin** are elevated roles that inherit all Active Member rights (see `00_master_plan.md`).

## Inputs
- **Login**: Email, Password.
- **Register**: Full Name, Email, Password, Confirm Password.
- **Password Reset**: Email.
- **Reset Confirm**: Token, New Password.

## Outputs
- **Success**: Auth Token (HttpOnly Cookie), User Profile JSON.
- **Failure**: Error Message (e.g., `auth.invalid_credentials`).

## Data Model (Conceptual)
- **User**: `id`, `email`, `password_hash`, `role` (default: 'Pending'), `status` (Pending, Active, Banned), `language_pref`, `created_at`.
- **Session**: `user_id`, `refresh_token_hash`, `expires_at`, `ip`, `user_agent`.
- **PasswordReset**: `token`, `user_id`, `expires_at`, `is_used`.

## Validation Rules
- **Email**: Valid format, unique.
- **Password**: Min 12 chars, mixed case, number, symbol.
- **CSRF**:
    - **Required**: For all state-changing *authenticated* requests (POST, PUT, PATCH, DELETE).
    - **Optional (Defense-in-depth)**: For public endpoints (Login, Register).

## Security & Permissions
- **Status Gating (CRITICAL)**:
    - **Rule**: `status == 'Active'` is the primary gate.
    - **Constraint**: Users with `status: Pending` MUST NOT access internal resources (Members, Calendar, Music), even if they are assigned a role like 'Musician' or 'Admin'. Role permissions only apply *after* status check passes.
- **Password Reset**:
    - **Enumeration Protection**: Always return "If this email exists, a link has been sent" regardless of existence.
    - **Token Security**: Single-use tokens. Short expiration (e.g., 15-60 mins).
    - **Invalidation**: Requesting a new reset invalidates all previous unused tokens for that user.
- **Rate Limiting**:
    - **Login**: 5 failed attempts per 15 min per IP/Account -> 15 min cooldown.
    - **Captcha**: Trigger reCAPTCHA/Turnstile after 3 failed attempts.
- **Audit**: Log `AUTH_LOGIN_SUCCESS`, `AUTH_LOGIN_FAIL`, `AUTH_LOGOUT`, `AUTH_REGISTER`, `AUTH_PASSWORD_RESET`.

## Execution (Placeholders)
- `execution/auth/login.py`
- `execution/auth/register.py`
- `execution/auth/refresh_session.py`
- `execution/auth/request_password_reset.py`
- `execution/auth/confirm_password_reset.py`

## Scope
### MVP
- Email/Password Login.
- Registration (Default to Pending Status).
- Admin Approval Workflow (Status Gating).
- Password Reset (Secure email flow).
- Role-based Access Control (RBAC).

### Phase 2
- Two-Factor Authentication (2FA).
- Social Login (Google/Apple).
- Device Management (View/Revoke sessions).
