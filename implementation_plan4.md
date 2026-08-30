# Implementation Plan - Stage 3: Moodle CSV Generator and Enrollment Management

This stage focuses on building the Moodle user ingestion CSV generator, database updates (marking pagos and moodle enrollment states), and creating an interactive dashboard to manage cursantes, apply filters, and trigger CSV downloads.

## User Review Required

> [!IMPORTANT]
> The moodle CSV generator will execute database updates (`estado_moodle = 'MATRICULADO'`) immediately upon generation of the CSV file. This is wrapped in a transaction block to ensure data consistency.
>
> The default password structure generated for new Moodle users is configured as `'Saavedra2026+'`.

## Proposed Changes

### 1. Moodle Integration Service
#### [NEW] [academico/services/moodle_generator.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/services/moodle_generator.py)
A service utility to extract paid and unmatriculated cursantes for a specific course:
- Columns: `username`, `password`, `firstname`, `lastname`, `email`, `cohort1`.
- Clean username (only digits).
- Check or generate fallback emails if blank (`{dni}@alumno.ariasdesaavedra.edu.ar`).
- Database update `estado_moodle = 'MATRICULADO'` inside `transaction.atomic()`.
- Return CSV data via a `HttpResponse` with attachments header.

### 2. Views and Endpoints
#### [MODIFY] [academico/views.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/views.py)
- **`lista_inscripciones`**: Dashboard query including counters (Total, Paid, Pending, Ready for Moodle) and filtering logic.
- **`marcar_pago`**: Endpoint expecting POST to mark payment as PAGADO, setting `fecha_pago = timezone.now()` and optionally log comprobante.
- **`descargar_csv_moodle`**: Endpoint to call `generate_moodle_csv` for a given course.

### 3. Routing
#### [MODIFY] [academico/urls.py](file:///c:/saavedra/gestor/gestion%20de%20aulas/academico/urls.py)
New routes mapping to the new views:
- `/academico/inscripciones/` -> `lista_inscripciones`
- `/academico/marcar-pago/<int:inscripcion_id>/` -> `marcar_pago`
- `/academico/descargar-moodle/<int:curso_id>/` -> `descargar_csv_moodle`

### 4. Interface Templates
#### [NEW] [templates/academico/gestion_inscripciones.html](file:///c:/saavedra/gestor/gestion%20de%20aulas/templates/academico/gestion_inscripciones.html)
Interactive HTML structure with:
- Summary count metrics.
- Filters by Course, Payment, Moodle state, and Search fields.
- Fast interactive buttons for individual payment marks.
- Conditional download button displaying how many unmatriculated paid cursantes exist for the course.

## Verification Plan

### Automated Tests
- Run `python manage.py check` to verify syntax.

### Manual Verification
- Upload test enrollments using the Syric loader.
- Verify status filtering on the Enrollment dashboard.
- Mark students as paid, checking if the counters update.
- Generate Moodle CSV and verify database status updates to `MATRICULADO`.
