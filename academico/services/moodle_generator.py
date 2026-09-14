import csv
import io
from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from academico.models import Curso, Inscripcion

def generate_moodle_csv_response(curso_id):
    """
    Genera un archivo CSV compatible con Moodle para matricular cursantes.
    Filtra por curso, estado_pago in ['PAGADO', 'BECADO_EXENTO'] y estado_moodle = 'NO_MATRICULADO'.
    Una vez generado, actualiza atomicamente el estado de moodle a 'MATRICULADO'.
    """
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Iniciar transacción atómica para asegurar consistencia
    with transaction.atomic():
        inscripciones = Inscripcion.objects.select_for_update().filter(
            curso=curso,
            estado_pago__in=['PAGADO', 'BECADO_EXENTO'],
            estado_moodle='NO_MATRICULADO'
        )
        
        if not inscripciones.exists():
            return None, f"No hay estudiantes con pago verificado listos para matricular en este curso."
        
        # Generar CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',')
        
        # Escribir cabeceras
        writer.writerow(['username', 'lastname', 'firstname', 'email', 'cohort1', 'password'])
        
        updated_ids = []
        for insc in inscripciones:
            cursante = insc.cursante
            
            # Limpiar DNI
            username = cursante.dni.strip().replace('.', '').replace(' ', '')
            
            # Contraseña por defecto
            password = 'Saavedra2026+'
            
            # Nombres capitalizados
            firstname = cursante.nombre.strip().title()
            lastname = cursante.apellido.strip().title()
            
            # Email o fallback
            email = cursante.email
            if not email or email.strip() == "":
                email = f"{username}@alumno.ariasdesaavedra.edu.ar"
            else:
                email = email.strip()
                
            # Cohorte Moodle del curso
            cohort1 = curso.id_cohorte_moodle or ""
            
            # Escribir fila
            writer.writerow([username, lastname, firstname, email, cohort1, password])
            updated_ids.append(insc.id)
            
        # Actualizar estado_moodle a 'MATRICULADO'
        Inscripcion.objects.filter(id__in=updated_ids).update(estado_moodle='MATRICULADO')
        
        # Preparar respuesta de descarga
        csv_data = output.getvalue()
        output.close()
        
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        codigo_curso = curso.id_syric or f"id_{curso.id}"
        filename = f"moodle_cohorte_{codigo_curso}_{fecha_str}.csv"
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response, None
