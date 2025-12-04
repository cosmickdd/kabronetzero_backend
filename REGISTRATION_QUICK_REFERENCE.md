"""
QUICK REFERENCE: Registration System API
==========================================

This is a one-page cheat sheet for the new registration and auth system.

REGISTRATION ENDPOINTS (All return 201 Created)
================================================

1. ORG_OWNER Registration
   POST /api/v1/auth/register/org-owner/
   Requires: email, password, full_name, organization details
   Response: user + organization context

2. BUYER Registration  
   POST /api/v1/auth/register/buyer/
   Requires: email, password, full_name, organization details
   Response: user + buyer_org context

3. Accept Invitation (ORG_MEMBER/MANAGER/DEVELOPER)
   POST /api/v1/auth/accept-invitation/
   Requires: invite_token, full_name, password
   Response: user + membership context

4. Create Validator (Admin-Only)
   POST /api/v1/auth/register/validator/
   Requires: admin auth, email, full_name, password (optional)
   Response: validator user

5. Create Regulator (Admin-Only)
   POST /api/v1/auth/register/regulator/
   Requires: admin auth, email, full_name, password (optional)
   Response: regulator user


LOGIN ENDPOINT
==============

POST /api/v1/auth/login/
Body: {
  "email": "user@example.com",
  "password": "password",
  "active_org_id": "org-uuid" (optional)
}
Response (200): {
  "access": "jwt-token",
  "refresh": "refresh-token",
  "user": { ... }
}

JWT CLAIMS in access token:
- sub: user ID
- global_role: ADMIN | REGULATOR | VALIDATOR | NORMAL_USER
- active_org_id: current org (optional)
- org_role: ORG_OWNER | MANAGER | MEMBER | DEVELOPER | BUYER (if org_id)


USER PROFILE ENDPOINTS
======================

GET /api/v1/auth/me/
→ Full user profile with organizations

PUT /api/v1/auth/me/update_profile/
Body: { "full_name": "...", "email": "..." }

GET /api/v1/auth/organizations/
→ List user's organizations

POST /api/v1/auth/organizations/set-active/
Body: { "organization_id": "org-uuid" }
→ Switch active organization


ORGANIZATION MEMBER MANAGEMENT
===============================

POST /api/v1/organizations/{org_id}/members/invite/
Headers: X-Org-Id: {org_id}
Permission: IsOrgOwnerOrManager
Body: {
  "email": "newmember@example.com",
  "role_in_org": "DEVELOPER",
  "message": "Join our team"
}
→ Returns: invitation token

GET /api/v1/organizations/{org_id}/members/
Headers: X-Org-Id: {org_id}
Permission: IsOrgMember
→ Returns: list of members

POST /api/v1/organizations/{org_id}/members/{member_id}/remove/
Headers: X-Org-Id: {org_id}
Permission: IsOrgOwner
Body: { "member_id": "member-uuid" }

PUT /api/v1/organizations/{org_id}/members/{member_id}/role/
Headers: X-Org-Id: {org_id}
Permission: IsOrgOwner
Body: { "role_in_org": "ORG_MANAGER" }


ROLE HIERARCHY
==============

GLOBAL ROLES (Platform Level):
- ADMIN: Full system access
- REGULATOR: Can override any decision
- VALIDATOR: Can validate all projects
- NORMAL_USER: Regular user (default for most)

ORGANIZATION ROLES (Per-Org):
- ORG_OWNER: Full org control, invite members
- ORG_MANAGER: Can invite, manage some settings
- ORG_MEMBER: Read-only member
- DEVELOPER: Can create/submit projects
- BUYER: Can purchase carbon credits


PERMISSION CLASSES
===================

ORG-SCOPED (require X-Org-Id header):
- IsOrgOwner: Only ORG_OWNER
- IsOrgOwnerOrManager: ORG_OWNER or ORG_MANAGER
- IsOrgMember: Any active member
- IsDeveloper: Only DEVELOPER role
- IsBuyer: Only BUYER role

PLATFORM-LEVEL (no org needed):
- IsRegulatorOrAdmin: global_role in [ADMIN, REGULATOR]
- IsValidator: global_role == VALIDATOR
- IsAdmin: global_role == ADMIN

USAGE:
```python
@permission_classes([IsOrgOwnerOrManager])
def invite_member(self, request):
    org_id = request.headers.get('X-Org-Id')
    # X-Org-Id automatically validated by permission class
```


REQUEST HEADERS
===============

Authorization: Bearer {access_token}
→ Required for all authenticated endpoints

X-Org-Id: {organization-uuid}
→ Required for org-scoped endpoints
→ Alternative: org_id query parameter

Content-Type: application/json
→ Standard for JSON requests


COMMON FLOWS
============

FLOW 1: Owner creates org and invites developer
─────────────────────────────────────────────
1. Owner: POST /register/org-owner/ → creates org
2. Owner: POST /members/invite/ (X-Org-Id: owner's org)
3. Developer: POST /accept-invitation/ → joins org
4. Developer: POST /login/ → gets JWT with org_role=DEVELOPER

FLOW 2: Buyer purchases credits
────────────────────────────────
1. Buyer: POST /register/buyer/ → creates buyer org
2. Buyer: POST /login/
3. Buyer: POST /purchases/ (X-Org-Id: buyer's org)

FLOW 3: Admin creates validator, validates project
──────────────────────────────────────────────────
1. Admin: POST /register/validator/ (admin auth required)
2. Validator: POST /login/
3. Validator: POST /projects/{id}/validate/
   (No X-Org-Id needed - global_role=VALIDATOR)

FLOW 4: Regulator overrides validation
───────────────────────────────────────
1. Regulator: POST /login/
2. Regulator: POST /projects/{id}/override-validation/
   (No X-Org-Id needed - global_role=REGULATOR)


HTTP STATUS CODES
=================

200 OK: Successful GET/PUT request
201 Created: Successful POST request (resource created)
400 Bad Request: Validation error in request
401 Unauthorized: Missing or invalid authentication
403 Forbidden: Authenticated but not permitted
404 Not Found: Resource not found
409 Conflict: Email already registered


COMMON ERRORS & SOLUTIONS
==========================

❌ "Invalid email or password"
→ Check email/password are correct
→ Check user.is_active = True (not frozen)

❌ "X-Org-Id header not provided"
→ Add X-Org-Id header to request
→ Or use org_id query parameter

❌ "You are not a member of this organization"
→ Check user is invited to org
→ Check membership.is_active = True

❌ "Only ORG_OWNER can perform this action"
→ Need ORG_OWNER role in that org
→ Check request has correct X-Org-Id

❌ "Email already registered"
→ User with that email exists
→ Use different email or login if exists

❌ "Invalid invite token"
→ Token expired (expires after 30 days)
→ Token already consumed (invitation accepted)
→ Generate new invitation


DATA MODELS QUICK REFERENCE
===========================

CustomUser:
├─ id: UUID
├─ email: unique string
├─ global_role: ADMIN | REGULATOR | VALIDATOR | NORMAL_USER
├─ active_org_id: UUID (current org context)
├─ is_active: bool
├─ is_verified: bool
├─ is_frozen: bool
└─ created_at, updated_at, last_login

Organization:
├─ id: ObjectId
├─ name: string
├─ type: industry | buyer_org | validator_org
├─ country, state, city: location
└─ created_by: CustomUser

OrganizationMembership:
├─ id: ObjectId
├─ user: CustomUser (FK)
├─ organization: Organization (FK)
├─ role_in_org: ORG_OWNER | MANAGER | MEMBER | DEVELOPER | BUYER
├─ is_active: bool
└─ created_at

OrganizationInvitation:
├─ id: ObjectId
├─ organization: Organization
├─ email: string
├─ role_in_org: string
├─ token: UUID (unique)
├─ is_consumed: bool
└─ expires_at: datetime


TESTING CHECKLIST
=================

□ Test each registration flow with valid data
□ Test registration with invalid email (not unique)
□ Test registration with mismatched passwords
□ Test login with correct credentials
□ Test login with wrong password
□ Test login with inactive user (is_frozen=True)
□ Test permission classes with X-Org-Id header
□ Test permission classes without X-Org-Id (should fail)
□ Test JWT token decoding and custom claims
□ Test token refresh endpoint
□ Test invite flow: create invite → accept
□ Test expired invitation token
□ Test consumed invitation token
□ Test ORG_OWNER can invite members
□ Test DEVELOPER cannot invite members
□ Test switch active organization
□ Test validator can validate across orgs
□ Test regulator can override decisions
□ Test permission denied (403) for unauthorized roles


DEPLOYMENT STEPS
================

1. Create Django migration:
   python manage.py makemigrations accounts

2. Run migration:
   python manage.py migrate accounts

3. Copy new files to production:
   - serializers_new.py → serializers.py
   - views_new.py → views.py
   - permissions_new.py → permissions.py
   - urls_new.py → urls.py

4. Update main urls.py:
   path('api/', include('apps.accounts.urls.py'))

5. Update settings.py:
   AUTH_USER_MODEL = 'accounts.CustomUser'

6. Test all endpoints on staging

7. Create initial admin/regulator via Django shell:
   from apps.accounts.models import CustomUser
   CustomUser.objects.create_superuser('admin@example.com', 'password')

8. Monitor logs for auth errors

9. Communicate new endpoints to front-end team


USEFUL COMMANDS
===============

# Create admin account
python manage.py shell
>>> from apps.accounts.models import CustomUser
>>> CustomUser.objects.create_superuser('admin@example.com', 'password')

# List all users
>>> CustomUser.objects.all().values('id', 'email', 'global_role')

# List organization members
>>> from apps.organizations.models import OrganizationMembership
>>> org_id = 'org-uuid-here'
>>> OrganizationMembership.objects.filter(organization_id=org_id, is_active=True)

# Freeze account
>>> user = CustomUser.objects.get(email='user@example.com')
>>> user.is_frozen = True
>>> user.freeze_reason = 'Suspicious activity'
>>> user.save()

# Unfreeze account
>>> user.is_frozen = False
>>> user.save()

# Check user permissions in org
>>> org_id = 'org-uuid'
>>> membership = OrganizationMembership.objects.get(user=user, organization_id=org_id)
>>> print(membership.role_in_org)


SECURITY NOTES
==============

✓ Passwords hashed using Django's PBKDF2 (default)
✓ JWT tokens use HS256 (SECRET_KEY based)
✓ Org scoping prevents cross-org data access
✓ Role-based permissions strictly enforced
✓ Headers (X-Org-Id) validated on each request
✓ Frozen accounts cannot login
✓ Email verification recommended before production

⚠ Don't share SECRET_KEY
⚠ Rotate refresh tokens periodically
⚠ Implement rate limiting on login endpoint
⚠ Log all admin actions (create validator, override, etc)
⚠ Monitor for frozen account attempts
⚠ Audit org member changes


API VERSIONING
==============

Current Version: v1
Endpoint Pattern: /api/v1/...

Future versions (if breaking changes):
/api/v2/... (backward incompatible)
/api/v1/... (maintained for 6+ months)


SUPPORT
=======

For issues or questions:
1. Check REGISTRATION_IMPLEMENTATION_GUIDE.md (detailed)
2. Check this quick reference
3. Review error messages and solutions above
4. Check application logs for detailed errors
5. Contact: [support email]
"""
