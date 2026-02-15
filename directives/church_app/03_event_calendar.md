# Directive: Event Calendar

## Purpose
Schedule and display church events, managing public visibility, audience targeting, and attendance.

## Roles
- **Staff/Admin**: Create/Edit/Delete Events.
- **Public**: View Public Events (ReadOnly).
- **Active Member**: View Internal Events, RSVP to eligible events.

## Inputs
- **Event**: Title, Description, StartTime (UTC), EndTime (UTC), Location, Visibility (Public/Internal), Target Audience (All, specific ministries), RSVP_Required.
- **RSVP**: Status (`rsvp.going`, `rsvp.maybe`, `rsvp.not_going`).

## Outputs
- Monthly Calendar View (i18n formatted dates).
- Event Detail Page.

## Data Model (Conceptual)
- **Event**: `id`, `title`, `description`, `start_at` (UTC), `end_at` (UTC), `is_public` (bool, default=False), `target_ministry_ids` (Array), `created_by`.
- **EventAttendee**: `event_id`, `user_id`, `status`, `updated_at`.

## Validation Rules
- **Title**: Required, Max 150 chars.
- **Timing**: `end_at` > `start_at`. Start time cannot be > 1 year in past.
- **Visibility**: `is_public` defaults to `false` (Secure-by-default). Internal events require `status=Active` to view.

## Security & Permissions
- **View Internal**: STRICTLY restricted to users with `status='Active'`. Pending users cannot view.
- **RSVP Cap**: Only `status='Active'` users can RSVP (prevents spam). Public users must log in/register to RSVP.
- **Create/Edit**: Staff/Admin only.
- **Audit**: Log `EVENT_CREATE`, `EVENT_UPDATE`, `EVENT_DELETE`, `RSVP_CHANGE`.

## Internationalization (i18n)
- **Timestamps**: Stored in UTC. Displayed converted to Viewer's local timezone.
- **Labels**: RSVP statuses and UI elements must use translation keys (e.g., `event.rsvp_going`).

## Execution (Placeholders)
- `execution/events/create_event.py`
- `execution/events/list_events.py`
- `execution/events/rsvp_action.py`

## Scope
### MVP
- Public vs Internal (Active-only) events.
- RSVP System (Authenticated Active Members only).
- Audience targeting (Global vs Ministry-specific).
- Timezone-aware date display.

### Phase 2
- Recurring Events.
- QRCode Check-in.
- Guest RSVP (with captcha/email verification).
