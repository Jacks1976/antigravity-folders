# Directive: Discussion Forum

## Purpose
Public boards for ministry updates, prayer requests, and community discussion.

## Roles
- **Admin**: Create Categories, Moderate content.
- **Member**: Create Topics, Reply.

## Inputs
- **Topic**: Title, Category, Body.
- **Reply**: TopicID, Body.

## Outputs
- Categorized Thread List.
- Thread View.

## Data Model (Conceptual)
- **Category**: `id`, `name`, `role_required` (e.g., 'Volunteers Only').
- **Topic**: `category_id`, `author_id`, `title`, `is_locked`.
- **Post**: `topic_id`, `author_id`, `body`.

## Validation Rules
- **Formatting**: Markdown supported (sanitized).

## Security & Permissions
- **View**: Role-based per Category.
- **Moderation**: Admin can Delete/Edit any post.

## Execution (Placeholders)
- `execution/forum/create_topic.py`
- `execution/forum/add_reply.py`

## Scope
### MVP (Structural Definition Only)
- This module is primarily Phase 2.
- MVP defines the Database Schema and Moderation Rules (Admin can delete).

### Phase 2
- Full implementation of UI/Logic.
- Rich Text Editor.
- User mentions (@user).
- "Like" reactions.
