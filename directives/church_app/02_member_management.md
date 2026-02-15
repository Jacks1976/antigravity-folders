# Directive: Member Management

## Purpose
Maintain the registry of church members, their extended profiles, and ministry assignments.

## Roles
- **Staff/Admin**: Full control over profiles and ministry assignments.
- **Ministry Lead**: Can assign members *only* to their own ministry.
- **Active Member**: Can view directory and edit certain fields of their own profile.

## Inputs
- **Profile Update**: Phone, Address, Birthday, Bio.
- **Admin/Lead Input**: Status Change (via Auth module), Ministry Assignment.

## Outputs
- **Member Directory**: Paginated list view.
- **Member Detail**: Full profile view.

## Data Model (Conceptual)
- **User (Auth)**: `id`, `email`, `status` (**Source of Truth**: Pending, Active, Banned).
- **MemberProfile**: `user_id` (FK), `full_name`, `phone`, `address`, `dob`, `baptism_date`, `bio`, `profile_pic_url`.
- **MinistryAssignment**: `member_id`, `ministry_id`, `role`, `assigned_by`, `start_date`.

## Validation Rules
- **Phone**: E.164 format.
- **DOB**: Not in future.
- **Status Sync**: Profile availability depends strictly on `User.status`.

## Security & Permissions

### Field-Level Permissions
| Field | Active Member (Self) | Staff/Admin | Directory Viewer (Other Members) |
| :--- | :--- | :--- | :--- |
| **Full Name** | Read-Only (Request Change) | Edit | View |
| **Email** | Read-Only | Edit | View |
| **Phone** | Edit | Edit | View (if public)* |
| **Address** | Edit | Edit | **Hidden** (PII) |
| **DOB** | Edit | Edit | View (Day/Month only) |
| **Baptism Date**| Read-Only | Edit | View |
| **Ministry** | Read-Only | Edit | View |

*\*Phone visibility can be toggled by user preference.*

### Directory Visibility
- **List View**: Name, Profile Pic, Ministry Badge.
- **Detail View**: Name, Bio, Phone (if shared), Ministry History, Birthday (Day/Month).
- **PII Protection**: Precise content (Address, Year of Birth) is **Staff-Only**.

### Ministry Assignment
- **Staff/Admin**: Can assign any user to any ministry.
- **Ministry Lead**: Can assign users *only* to the ministries they lead. (Phase 2 constraint checks).

## Execution (Placeholders)
- `execution/members/create_profile.py`
- `execution/members/update_profile.py`
- `execution/members/assign_ministry.py`
- `execution/members/get_directory.py`

## Scope
### MVP
- CRUD operations for Member Profiles.
- Status management via Auth User model.
- Directory Listing (List/Detail views).
- Staff/Admin Ministry Assignment.

### Phase 2
- Ministry Lead specific permissions.
- Detailed Ministry History / Timeline.
- Family Grouping.
