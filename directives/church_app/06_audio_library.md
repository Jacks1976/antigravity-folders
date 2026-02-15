# Directive: Audio & File Infrastructure

## Purpose
Provide a secure, shared infrastructure for storing and serving worship-related files (MP3s for audio, PDFs for chord charts). This module handles storage, access control, and auditing, while domain-specific associations (e.g., linking a file to a Song) are handled by modules like `05_music_repertoire.md`.

## Roles
- **GL Moderator (Worship Leader)**:
    - **Rights**: Upload new files, Delete files.
    - **Check**: `status='Active'` AND (`role='Staff/Admin'` OR `MinistryAssignment.is_lead=true`).
- **Musician**:
    - **Rights**: Download files, Stream audio.
    - **Check**: `status='Active'` AND `MinistryAssignment` exists for Worship Team.
- **System**: Generates secure links.

## Inputs
- **File**: Binary content (MP3 or PDF).
- **Metadata**: Content-Type, Filename.

## Outputs
- **Secure Link**: Time-limited Signed URL (for download/streaming).

## Data Model (Conceptual)
- **Asset**: `id`, `filename`, `storage_path` (S3 key or local path), `size_bytes`, `mime_type`, `uploaded_by` (User ID), `created_at`.
    - *Note: No song titles or artist names here. Those live in `05_music_repertoire`.*

## Validation Rules
- **Allowed Types**: `.mp3` (Audio), `.pdf` (Chord Charts/Sheet Music).
- **Size Limit**: 
    - MP3: Max 20MB.
    - PDF: Max 10MB.
- **Storage**: Files must be stored in a non-public directory or private S3 bucket.

## Security & Permissions
- **Access Gate**: STRICTLY restricted to internal users with `status='Active'`.
- **Download/Stream**:
    - Never expose raw file paths or public URLs.
    - Use **Short-lived Signed URLs** (e.g., expires in 1 hour).
    - Permission check required *before* generating link.
- **Upload/Delete**: Restricted to Staff/Admin or Worship Moderators.
- **Audit**: Log `ASSET_UPLOAD`, `ASSET_DOWNLOAD`, `ASSET_DELETE` (with `actor_id` and `asset_id`).

## Internationalization (i18n)
- **UI Strings**: Validation errors and upload dialogs must use translation keys (e.g., `files.upload_success`, `files.error_too_large`).

## Execution (Placeholders)
- `execution/files/upload_asset.py`
- `execution/files/delete_asset.py`
- `execution/files/get_signed_url.py`

## Scope
### MVP
- Support MP3 and PDF formats.
- Local filesystem storage (secured) OR S3.
- Signed URL generation.
- Role-based Upload/Delete (Moderator only).

### Phase 2
- Image support (JPG/PNG).
- Video support (with streaming optimization).
- Virus scanning on upload.
