# Implementation Plan - Stage 1: Enrollment and Academic Management System

This plan outlines the setup of the Django project `core_gestion`, the `academico` application, MySQL database configuration using environment variables, data models, and Django Admin customization.

## User Review Required

> [!IMPORTANT]
> The MySQL/MariaDB database must exist on the target system for the migrations to run. In the verification section, we've provided instructions to create the database (`gestion_cursos` or similar name).
>
> We will configure `mysqlclient` as the primary driver, with a fallback import of `pymysql` if `mysqlclient` is not installed.

## Open Questions
- No open questions. The specifications provided are highly detailed.

## Proposed Changes

### Project Setup and Configuration

#### [NEW] [.env.example](file:///c:/saavedra/gestor/gestion_cursos/.env.example)
Example environment variables file, including Database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) and Django settings (`SECRET_KEY`, `DEBUG`, etc.).

#### [NEW] [requirements.txt](file:///c:/saavedra/gestor/gestion_cursos/requirements.txt)
Dependencies required for the project, such as `Django`, `python-dotenv`, `mysqlclient`, and `pymysql`.

### Django Core Application

#### [NEW] [settings.py](file:///c:/saavedra/gestor/gestion_cursos/core_gestion/settings.py)
Django configuration:
- Load `.env` using `python-dotenv`.
- Configure `DATABASES` using `django.db.backends.mysql` and env variables.
- Configure static and media assets.
- Register `academico` and any other default Django apps.

#### [NEW] [__init__.py](file:///c:/saavedra/gestor/gestion_cursos/core_gestion/__init__.py)
Initialize fallback for PyMySQL if `mysqlclient` is not installed.

### Academic Application

#### [NEW] [models.py](file:///c:/saavedra/gestor/gestion_cursos/academico/models.py)
Contains models:
- `Curso` (id_syric, nombre, id_cohorte_moodle, arancel, dates, active, ManyToMany to User as docentes)
- `Cursante` (dni, nombre, apellido, email, telefono, fecha_nacimiento, titulo_previo)
- `Inscripcion` (cursante, curso, id_preinscripcion_syric, estado_pago, fecha_pago, comprobante_pago, estado_moodle, estado_academico, nota_final, certificado_syric, observations, unique_together constraint)

#### [NEW] [admin.py](file:///c:/saavedra/gestor/gestion_cursos/academico/admin.py)
Register models in Django Admin with comprehensive lists, search fields, filters, and fieldsets.

## Verification Plan

### Automated Tests & CLI Checks
- Execute `python manage.py check` to verify configuration syntax.
- Execute `python manage.py makemigrations` and `python manage.py migrate` (after database configuration) to test database driver compatibility and DDL generation.

### Manual Verification
- Access Django Admin, create instances of `Curso`, `Cursante`, and `Inscripcion` to verify validations, constraints (`unique_together`), and display representations.
