# Walkthrough - Django Project Setup & Syric Integration

All components for the academic enrollment management system have been successfully created, configured, migrated, and verified.

## Accomplished Tasks

### 1. Project Initialization & Dependencies
- Created local virtual environment `.venv` inside workspace directory.
- Installed required packages: `django`, `pymysql`, `cryptography`, `python-dotenv`, `pandas`, `openpyxl`, and `mysqlclient`.
- Initialized Django project `core_gestion` and app `academico`.

### 2. Database & Variables Config
- Created [db_init.sql](file:///c:/saavedra/gestor/gestion%20de%20aulas/db_init.sql) for database generation.
- Created [.env.example](file:///c:/saavedra/gestor/gestion%20de%20aulas/.env.example) and loaded [.env](file:///c:/saavedra/gestor/gestion%20de%20aulas/.env) containing MariaDB credentials.
- Connected to MariaDB successfully and initialized `gestion_cursos` database.

### 3. Application Architecture & Models
- Built [models.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/models.py) comprising:
  - `Curso` (DNI index, price, dates, teachers).
  - `Cursante` (Unique DNI, contacts, title).
  - `Inscripcion` (Payment status, moodle status, final grade, syric certificate status).
- customized [admin.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/admin.py) with advanced listing search fields and filters.
- Built [syric_parser.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/services/syric_parser.py) service using pandas for parsing Excel/CSV files, cleaning DNI, separating contacts, and executing `update_or_create`.
- Designed [importar_syric.html](file:///c:/saavedra/gestor/gestion%20de%20aulas/templates/academico/importar_syric.html) template with Bootstrap 5 cards and results tables.
- Programmed login page template [login.html](file:///c:/saavedra/gestor/gestion%20de%20aulas/templates/registration/login.html).

### 4. Database Migrations & Administration Setup
- Executed `makemigrations` and `migrate` using native `mysqlclient`.
- Created admin superuser:
  - **Usuario:** `admin`
  - **Contraseña:** `admin123`

### 5. Verification
The local server is running at `http://127.0.0.1:8000/`. Verification via python requests confirms the following path behavior:
- `http://127.0.0.1:8000/academico/importar-syric/` properly redirects to `/login/?next=/academico/importar-syric/` (Status `200` OK).
- `http://127.0.0.1:8000/admin/` properly redirects to `/admin/login/?next=/admin/` (Status `200` OK).
