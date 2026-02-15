# Directive: Internal Messaging

## Purpose
Enable private, direct communication between church members.

## Roles
- **Active Member/Staff**: Can send and receive messages.
- **Public**: No access.

## Inputs
- **Message**: RecipientID, BodyContent.

## Outputs
- Inbox View.
- Chat UI.

## Data Model (Conceptual)
- **Message**: `id`, `sender_id`, `recipient_id`, `body`, `sent_at`, `read_at`.

## Validation Rules
- **Self-send**: Block sending to self.
- **Content**: Max length 2000 chars. No HTML allowed.

## Security & Permissions
- **Privacy**: Messages viewable ONLY by sender and recipient (and Admin for moderation audit).
- **Harassment**: Block feature required (Phase 2, but DB field in MVP).

## Execution (Placeholders)
- `execution/messaging/send_dm.py`
- `execution/messaging/get_inbox.py`

## Scope
### MVP
- 1-on-1 Direct Messages (Text only).
- Unread count.

### Phase 2
- Group Chats.
- Image/File Attachments.
- "Block User" functionality.
