# Implementation Plan - Academic and Enrollment Management System with Syric Parser

This plan covers the initialization of the Django environment, MariaDB database setup, data modeling, parser service for Syric Excel/CSV files, import views, templates with Bootstrap 5, and validation.

## User Review Required

> [!IMPORTANT]
> The database connection is configured to point to a local MariaDB/MySQL database (`127.0.0.1:3306`, user: `root`, database: `gestion_cursos`). You must execute the provided SQL script to create the database before migrations can be run.
>
> PyMySQL is used with Django using `pymysql.install_as_MySQLdb()` in `core_gestion/__init__.py`.

## Open Questions
- None at this stage. All requirements (models, fields, parser constraints, and UI specifications) are fully defined.

## Proposed Changes

### 1. Database Initialization
#### [NEW] [db_init.sql](file:///c:/saavedra/gestor/gestion%20de%20aulas/db_init.sql)
SQL query to create the database `gestion_cursos` with UTF-8 support:
```sql
CREATE DATABASE IF NOT EXISTS gestion_cursos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Environment & Dependencies Setup
#### [NEW] [requirements.txt](file:///c:/saavedra/gestor/gestion%20de%20aulas/requirements.txt)
Define project dependencies: `django`, `pymysql`, `cryptography`, `python-dotenv`, `pandas`, `openpyxl`.

#### [NEW] [.env.example](file:///c:/saavedra/gestor/gestion%20de%20aulas/.env.example)
Example environment configurations: DB details, Django secret key, debug status.

#### [NEW] [.env](file:///c:/saavedra/gestor/gestion%20de%20aulas/.env)
Active environment variables (will use safe defaults for development).

### 3. Django Project (`core_gestion`)
#### [NEW] [core_gestion/__init__.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/core_gestion/__init__.py)
Imports and executes `pymysql.install_as_MySQLdb()` to compatibility-patch Django's DB client.

#### [NEW] [core_gestion/settings.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/core_gestion/settings.py)
Django configuration:
- Load `.env` file.
- Configure MySQL engine using PyMySQL.
- Setup login URLs, template directories, static/media folders.
- Register `academico` application.

#### [NEW] [core_gestion/urls.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/core_gestion/urls.py)
Root URL routing, including admin dashboard and the academico import view.

### 4. Academico Application
#### [NEW] [academico/models.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/models.py)
Data models:
- `Curso`: Syric id, name, moodle cohorte, price, dates, status, teachers (ManyToMany with Django's `User`).
- `Cursante`: Unique index DNI, name, surname, email, phone, birthday, previous degree.
- `Inscripcion`: Relation of Cursante and Curso, pre-registration ID, payment state, payment date, invoice, moodle state, academic status, final grade, syric certificate status, registration date, notes. Unique constraints on `('cursante', 'curso')`.

#### [NEW] [academico/admin.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/admin.py)
Register models in Django administration with advanced filters, search, and list views.

#### [NEW] [academico/services/syric_parser.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/services/syric_parser.py)
Service parsing logic for `.xlsx`, `.xls` and `.csv`:
- Load file with pandas.
- Standardize headers/data.
- Clean DNI (only numbers, no dots).
- Parse combined `CONTACTOS` field using regular expressions to extract email and telephone.
- Convert date fields into `YYYY-MM-DD` standard format.
- Execute `update_or_create` on database rows inside a transaction, logging new/updated rows vs errors.

#### [NEW] [academico/views.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/views.py)
`importar_syric` view:
- Request method POST: checks files, processes parsing.
- Login requirement using `@login_required`.
- Feedback context containing stats (total records, created/updated, errors).

#### [NEW] [academico/urls.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/urls.py)
Application-specific routes.

#### [NEW] [templates/academico/importar_syric.html](file:///c:/saavedra/gestor/gestion%20de%20aulas/templates/academico/importar_syric.html)
Bootstrap 5 styled upload form with error log tables, summary stats, and course selectors.

## Verification Plan

### Automated Tests
- Run `python manage.py check` to verify syntax and Django settings.
- Run `python manage.py makemigrations` and `python manage.py migrate` inside the virtual environment.

### Manual Verification
- Access `/admin/` and `/academico/importar-syric/` interfaces.
- Test import with a dummy Excel file containing Syric format data (contacts, DNI with dots, etc.).
