# Directive: Music Rehearsal Scheduling

## Purpose
Manage musician scales (rosters), rehearsal times, and service setlists. Integrates with **Event Calendar** for dates and **Music Repertoire** for songs.

## Roles
- **GL Moderator (Worship Leader)**:
    - **Rights**: Create Schedules, Assign Musicians, Override Status, Edit Setlists.
    - **Check**: `status='Active'` AND (`role='Staff/Admin'` OR `MinistryAssignment.is_lead=true` for Worship).
- **Musician**:
    - **Rights**: View Schedule, Accept/Decline *Own* Assignments, View Setlist.
    - **Check**: `status='Active'` AND `MinistryAssignment` exists for Worship Team.

## Inputs
- **Service Plan**: Date/Time, Linked Event ID (Optional), Setlist (Ordered Songs).
- **Assignment**: Instrument, MusicianUser.

## Outputs
- **Interactive Roster**: Calendar view with status indicators (Pending/Confirmed/Declined).
- **My Schedule**: Personal dashboard for musicians.

## Data Model (Conceptual)
- **ServicePlan**: `id`, `date`, `event_id` (FK to `03_event_calendar`-Optional), `notes`, `created_by`.
- **ServiceSetlist**: `plan_id`, `song_id` (FK to `05_music_repertoire`), `orderIndex`.
- **RosterEntry**: `plan_id`, `musician_id`, `instrument`, `status` (Pending/Confirmed/Declined/Overridden).

## Validation Rules
- **Conflict**: Warn if musician is already booked or declined for that time.
- **Setlist**: Songs must exist in `05_music_repertoire`.
- **Capacity**: logic to prevent over-booking (e.g., max 1 drummer) per service is recommended.

## Security & Permissions
- **Access Gate**: STRICTLY restricted to internal users with `status='Active'`. Permissions invalid otherwise.
- **Musician Actions**: Can ONLY update `status` for their *own* `musician_id` entries.
- **Moderator Actions**: Full CRUD on Plans, Setlists, and Roster. Can override Roster Status.
- **Audit**: Log `ROSTER_CREATE`, `ROSTER_UPDATE`, `ROSTER_ASSIGN`, `ROSTER_CONFIRM`, `ROSTER_DECLINE`.

## Execution (Placeholders)
- `execution/music/create_roster.py`
- `execution/music/update_roster_status.py`
- `execution/music/manage_setlist.py`

## Scope
### MVP
- Manual Service Plan creation.
- Setlist selection (Song IDs).
- Roster Assignment.
- Musician Dashboard (Accept/Decline).

### Phase 2
- Auto-scheduling algorithm (Rotation/Availability).
- Integration with external song databases (CCLI).
- Notification system (Email/Push) for assignments.
