# Directive: Music Repertoire ("Nosso Repertório")

## Purpose
Centralize the management of worship songs, including chord charts, sheet music, audio references, and external links. Provides targeted study materials for the Worship Team.

## Roles
- **GL Moderator (Worship Leader)**:
    - **Definition**: Active Member with `MinistryAssignment` for the Worship Team where `is_lead=true`.
    - **Rights**: Create/Edit/Delete songs. Upload files. Manage instrument tags.
- **Musician**:
    - **Definition**: Active Member with `MinistryAssignment` for the Worship Team (any role).
    - **Rights**: View/Search repertoire. Access assets for their instrument/role.
- **Staff/Admin**: Full permissions (Inherits Moderator rights).
- **Non-Musician**: **No Access**.

## Inputs
- **Song Metadata**: Title, Artist, Key (Original/Arrangement), Tempo (BPM), Tags (Theme, Speed).
- **Asset**: Type (Link/File), Category (PDF, MP3, YouTube), URL or FileBlob, Target Instruments.

## Outputs
- **Repertoire List**: Searchable/Filterable by Title, Key, Tag.
- **Song Detail View**: Metadata + Organized Asset List (highlighting user's instrument).

## Data Model (Conceptual)
- **Song**: `id`, `title`, `artist`, `bpm`, `default_key`, `created_at`.
- **SongAsset**: `id`, `song_id`, `type` (LINK, FILE), `url` (Links), `audio_asset_id` (Files - FK to `06_audio_library`), `label` (e.g., "Bass Tab"), `instrument_tags`.
- **InstrumentTag**: `id`, `name` (e.g., Vocal, Guitar, Drums).
- **MinistryAssignment (Ref)**: Used for permission check (`role='Musician'`, `is_lead=true/false`).

## Validation Rules
- **Duplicates**: Warn if Song Title + Artist already exists.
- **Keys**: Must be valid musical keys (C, C#, Db, etc.).
- **File Storage**:
    - **Links**: YouTube/Drive URLs (Metadata only).
    - **Files**: All uploads managed via `06_audio_library.md`. Size limits and storage paths defined there.

## Security & Permissions
- **Access Gate**:
    - User must have `status='Active'`.
    - User must have a valid **MinistryAssignment** to the "Worship Team".
- **Moderator Actions** (Create/Edit/Upload):
    - Requester must be **Staff/Admin** OR have `MinistryAssignment.is_lead=true` for the Worship Team.
- **Public Access**: **None**.
- **Audit**: Log `SONG_CREATE`, `SONG_UPDATE` (File events logged by `06_audio_library`).

## Internationalization (i18n)
- **UI Strings**: All headers, buttons, labels must use translation keys (e.g., `music.add_song`, `music.key`).
- **Content**: Song titles/lyrics remain in original language (English/Portuguese).
- **Tags**: Instrument names should be localized.

## Execution (Placeholders)
- `execution/music/create_song.py`
- `execution/music/add_asset.py`
- `execution/music/list_repertoire.py`

## Scope
### MVP
- Song Metadata Management.
- External Link support (YouTube/Spotify).
- Internal PDF/MP3 Upload.
- Instrument Tagging for Assets.
- Role-based Search/View (Moderator vs Musician).

### Phase 2
- Transposition Tools (On-the-fly chord chart transposition).
- Setlist Builder (Integration with `05_music_scheduling`).
- Lyrics Projection Mode.
