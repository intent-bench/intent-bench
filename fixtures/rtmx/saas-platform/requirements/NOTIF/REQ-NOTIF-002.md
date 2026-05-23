# REQ-NOTIF-002: Automated Lifecycle Notifications

## Status: MISSING
## Priority: HIGH
## Phase: 5

## Requirement

Implement automated notification generation for key lifecycle events across the platform. The system must automatically create notifications for affected users when specific organization, membership, project, and billing events occur. This ensures that members are kept informed of changes that affect their access, projects, and billing without requiring manual notification creation.

## Acceptance Criteria

1. When a user receives an invitation, a notification of type "invitation_received" is created for the invited user.
2. When an invitation is accepted, a notification of type "invitation_accepted" is created for the user who sent the invitation.
3. When a member's role is changed, a notification of type "role_changed" is created for the affected member.
4. When a member is removed from an organization, a notification of type "member_removed" is created for the removed user.
5. When a project is archived, a notification of type "project_archived" is created for all members of the organization.
6. When a project is deleted, a notification of type "project_deleted" is created for all members of the organization.
7. When an organization's billing plan is changed, a notification of type "plan_changed" is created for the organization owner.
8. When usage reaches 80% of a plan limit, a notification of type "quota_warning" is created for organization owners and admins.
9. Each automated notification includes a descriptive title and body with relevant context (org name, project name, role, etc.).
10. Automated notifications are created asynchronously and do not block the triggering API response.

## API Endpoints

Not applicable. This requirement covers automatic notification creation triggered by other endpoints. Notifications are accessed via the endpoints defined in REQ-NOTIF-001.

### Example notification payloads

**Invitation received:**
```json
{
  "type": "invitation_received",
  "title": "Organization Invitation",
  "body": "You have been invited to join Acme Corp as a member."
}
```

**Role changed:**
```json
{
  "type": "role_changed",
  "title": "Role Updated",
  "body": "Your role in Acme Corp has been changed to admin."
}
```

**Plan changed:**
```json
{
  "type": "plan_changed",
  "title": "Plan Updated",
  "body": "Acme Corp plan has been changed from starter to business."
}
```

**Quota warning:**
```json
{
  "type": "quota_warning",
  "title": "Usage Limit Warning",
  "body": "Acme Corp has used 82% of its project quota (41 of 50)."
}
```

## Dependencies

- REQ-NOTIF-001: Requires the notification system infrastructure for creating and storing notifications.
