from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_principal, name='dashboard_principal'),
    path('importar-syric/', views.importar_syric, name='importar_syric'),
    path('inscripciones/', views.lista_inscripciones, name='lista_inscripciones'),
    path('marcar-pago/<int:inscripcion_id>/', views.marcar_pago, name='marcar_pago'),
    path('descargar-moodle/<int:curso_id>/', views.descargar_csv_moodle, name='descargar_csv_moodle'),
    path('marcar-mail-enviado/<int:inscripcion_id>/', views.marcar_mail_enviado, name='marcar_mail_enviado'),
    path('detalle-inscripcion/<int:inscripcion_id>/', views.detalle_inscripcion, name='detalle_inscripcion'),
    path('guardar-observacion/<int:inscripcion_id>/', views.guardar_observacion, name='guardar_observacion'),
    path('cursante/editar/<int:cursante_id>/', views.editar_cursante, name='editar_cursante'),
    
    # ETAPA 4
    path('portal-docente/', views.portal_docente, name='portal_docente'),
    path('acta/<int:curso_id>/', views.acta_calificaciones, name='acta_calificaciones'),
    path('reporte-syric/', views.reporte_syric, name='reporte_syric'),
    path('descargar-aprobados/<int:curso_id>/', views.descargar_aprobados_syric, name='descargar_aprobados_syric'),
]
