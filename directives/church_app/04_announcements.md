# Directive: Announcements

## Purpose
Broadcast important messages to specific segments of the congregation.

## Roles
- **Staff/Admin**: Compose and Pin messages.
- **Ministry Leader**: Announce to their ministry.
- **Active Member**: View assigned announcements.

## Inputs
- **Announcement**: Title, Body, ExpirationDate, TargetAudience (Global, Role:X, Ministry:Y), IsPinned.

## Outputs
- Dashboard Feed of active announcements.

## Data Model (Conceptual)
- **Announcement**: `id`, `title`, `body`, `target_type` (Global/Role/Ministry), `target_id`, `expires_at`.
- **ReadReceipt**: `announcement_id`, `user_id`, `read_at` (Optional MVP analytics).

## Validation Rules
- **Expiration**: Must be in future.
- **Precedence**: `ExpirationDate` **always** overrides `IsPinned` (Expired pinned items must not display).
- **Target**: Valid Ministry/Role ID required if not Global.

## Security & Permissions
- **View Access**: STRICTLY restricted to users with `status='Active'`. Pending users cannot view announcements.
- **View Scope**: Users see only Global + Assignments (Role/Ministry) matching their profile.
- **Create Global**: Admin only.
- **Create Ministry**: Admin or Ministry Leader.
- **Audit**: Log `ANNOUNCEMENT_CREATE`, `ANNOUNCEMENT_UPDATE`, `ANNOUNCEMENT_DELETE`, `ANNOUNCEMENT_PIN`.

## Execution (Placeholders)
- `execution/announcements/post_message.py`
- `execution/announcements/get_feed.py`

## Scope
### MVP
- Pinned Messages (overridden by expiration).
- Segmentation by Role (e.g., "Musicians") AND Ministry (e.g., "Kids Ministry").
- Auto-hide after expiration.
- ReadReceipts (Analytics only - no enforcement/blocking).

### Phase 2
- Push Notifications.
- Rich Text/HTML support.
- "Must Read" acknowledgement enforcement (Blocking UI).
