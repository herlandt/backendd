# Copilot Instructions for backendd

## Project Overview
This is a Django-based backend for a condominium management system. The codebase is organized by domain modules (e.g., `condominio`, `finanzas`, `seguridad`, `usuarios`, etc.), each containing models, views, serializers, permissions, and tests. The main configuration is in `config/settings.py`.

## Architecture & Patterns
- **App Structure:** Each domain (e.g., `seguridad`, `condominio`) is a Django app with its own models, views, serializers, and tests.
- **Permissions:** Custom permissions (see `seguridad/permissions.py`) use API keys and user roles. Example: `HasAPIKey` checks for `X-API-KEY` in headers against `settings.SECURITY_API_KEY`.
- **Testing:** Tests are in each app's `tests.py`. Use Django's `APITestCase` for API endpoints. Example: `PermissionsTests` in `seguridad/permissions.py`.
- **Services:** Business logic is often separated into `services.py` within each app.
- **Serializers:** Data validation and transformation are handled in `serializers.py`.
- **Migrations:** Each app has its own `migrations/` folder for database schema changes.
- **Advanced Filtering:** All ViewSets implement django-filter with comprehensive field filtering, text search, and ordering capabilities. See `FILTROS_API.md` for complete documentation.

## Developer Workflows
- **Run Server:**
  ```powershell
  python manage.py runserver
  ```
- **Run Tests:**
  ```powershell
  python manage.py test
  ```
- **Apply Migrations:**
  ```powershell
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Build/Deploy:**
  - Use `build.sh` for custom build steps (if needed).
  - `render.yaml` and `passenger_wsgi.py` are for deployment (e.g., Render, Passenger).

## Conventions & Integration
- **API Key Security:** Endpoints requiring extra security use the `HasAPIKey` permission.
- **Role-Based Access:** Roles (e.g., RESIDENTE, GUARDIA, ADMIN) are checked via custom permissions (see commented examples in `seguridad/permissions.py`).
- **Static Files:** Served from `staticfiles/`.
- **External Scripts:** AI/ML scripts are in `ia_scripts/` (e.g., `face_camera.py`).
- **Cross-App Communication:** Use Django ORM for relations (e.g., `Propiedad` in `condominio` references `User`).

## Key Files & Directories
- `config/settings.py`: Main Django settings
- `manage.py`: Entry point for Django commands
- `seguridad/permissions.py`: Custom permissions and tests
- `condominio/models.py`: Example of domain models
- `ia_scripts/`: AI/ML related scripts
- `FILTROS_API.md`: Complete documentation of API filtering capabilities

## Example Patterns
- **Custom Permission:**
  ```python
  class HasAPIKey(BasePermission):
      def has_permission(self, request, view):
          expected = getattr(settings, "SECURITY_API_KEY", None)
          provided = request.headers.get("X-API-KEY") or request.META.get("HTTP_X_API_KEY")
          return bool(expected) and provided == expected
  ```
- **Test Case:**
  ```python
  class PermissionsTests(APITestCase):
      def test_staff_can_access_endpoint(self):
          self.client.force_authenticate(user=self.staff_user)
          response = self.client.post(self.url_control_acceso, {"placa": "NOEXISTE"})
          self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
  ```

---
If any section is unclear or missing, please specify which workflows, patterns, or integrations need more detail.