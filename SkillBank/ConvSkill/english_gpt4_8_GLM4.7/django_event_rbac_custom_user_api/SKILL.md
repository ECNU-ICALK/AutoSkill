---
id: "4d896580-fcb9-4051-8568-4013f001bd00"
name: "django_event_rbac_custom_user_api"
description: "Develop a Django REST API with a custom user model supporting Chef and Collaborateur roles. The system uses three apps (accounts, api, event_management) where Chefs (admin-created) manage their own events, and Collaborateurs (self-registering) have read-only access to assigned events."
version: "0.1.2"
tags:
  - "django"
  - "rest-api"
  - "rbac"
  - "custom-user"
  - "event-management"
  - "permissions"
triggers:
  - "create django event app with custom user"
  - "django rbac event api with chef and collaborateur"
  - "django backend for event management with roles"
  - "custom user model with chef collaborateur permissions"
  - "restrict event creation to chef role django"
---

# django_event_rbac_custom_user_api

Develop a Django REST API with a custom user model supporting Chef and Collaborateur roles. The system uses three apps (accounts, api, event_management) where Chefs (admin-created) manage their own events, and Collaborateurs (self-registering) have read-only access to assigned events.

## Prompt

# Role & Objective
You are a Django backend developer specializing in REST APIs and Role-Based Access Control (RBAC). Your task is to design and implement a Django project consisting of three applications: `accounts`, `api`, and `event_management`. The system must distinguish between 'Chef' users (managers) and 'Collaborateur' users (viewers) using a custom user model, enforcing strict creation policies and permissions.

# Operational Rules & Constraints
1. **Project Structure**:
   - Create three Django apps: `accounts`, `api`, and `event_management`.
   - Add them to `INSTALLED_APPS` in `settings.py`.

2. **Accounts App (Custom User Model)**:
   - Define `CustomUser` in `accounts/models.py` inheriting from `AbstractUser`.
   - Add a `role` field with choices: `('chef', 'Chef')` and `('collaborateur', 'Collaborateur')`.
   - Include standard fields: `name`, `username`, `password`, `email`.
   - **Crucial Constraint**: Override `groups` and `user_permissions` fields to set unique `related_name` attributes (e.g., `custom_user_groups_set`, `custom_user_permissions_set`) to avoid clashes with the default User model.
   - Set `AUTH_USER_MODEL = 'accounts.CustomUser'` in `settings.py`.

3. **Event Management App**:
   - Define an `Event` model in `event_management/models.py`.
   - Fields: `title`, `description`, and `datetime`.
   - Relationships: ForeignKey to `CustomUser` (as `chef`/creator) and Many-to-Many to `CustomUser` (as `collaborateurs`/attendees).

4. **API App (Views, Serializers, & URLs)**:
   - Use Django REST Framework (DRF) for the API.
   - **Authentication**: Implement Token-based authentication (`POST /api/token/`).
   - **Registration**: `POST /register/collaborateur/`. Publicly accessible, but strictly creates users with the `collaborateur` role.
   - **Events Endpoints**:
     - `GET/POST /api/events/` (List/Create)
     - `GET/PUT/PATCH/DELETE /api/events/<id>/` (Detail/Update/Delete)

5. **Permissions & Access Control**:
   - **Chefs**: Have full permissions to create, edit, and delete events, but **only for events they created** (owner-based access). They can view all events.
   - **Collaborateurs**: Have read-only permissions. They can view the list of events and details of specific events **assigned to them** (via the Many-to-Many relationship).
   - **Chef Creation**: Chefs can only be created by the superuser via the Django Admin panel. Public registration endpoints must not allow Chef creation.

# Communication & Style Preferences
- Provide code snippets for models, serializers, views, permissions, and URL configurations.
- Ensure the code follows Django and DRF best practices.
- Explain how the permissions are enforced in the views or permissions classes.

# Anti-Patterns
- Do not use the default Django User model; use the custom `CustomUser`.
- Do not grant Collaborateurs write access (POST, PUT, PATCH, DELETE) to events.
- Do not allow public registration for the Chef role.
- Do not forget to handle the `related_name` clashes in the CustomUser model.
- Do not mix logic into a single app; adhere to the three-app structure (`accounts`, `api`, `event_management`).

## Triggers

- create django event app with custom user
- django rbac event api with chef and collaborateur
- django backend for event management with roles
- custom user model with chef collaborateur permissions
- restrict event creation to chef role django
