from django.contrib import admin
from .models import Curso, Cursante, Inscripcion, TituloCursante

class TituloCursanteInline(admin.TabularInline):
    model = TituloCursante
    extra = 1

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id_syric', 'nombre', 'id_cohorte_moodle', 'arancel', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('activo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('id_syric', 'nombre', 'id_cohorte_moodle')
    filter_horizontal = ('docentes',)
    fieldsets = (
        ('Información General', {
            'fields': ('id_syric', 'nombre', 'arancel', 'activo')
        }),
        ('Integración Moodle', {
            'fields': ('id_cohorte_moodle',)
        }),
        ('Fechas del Curso', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Asignación de Personal', {
            'fields': ('docentes',)
        }),
    )


@admin.register(Cursante)
class CursanteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido', 'nombre', 'email', 'telefono', 'fecha_nacimiento', 'titulo_previo')
    search_fields = ('dni', 'nombre', 'apellido', 'email', 'telefono')
    ordering = ('apellido', 'nombre')
    inlines = [TituloCursanteInline]



@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = (
        'cursante', 
        'curso', 
        'id_preinscripcion_syric', 
        'estado_pago', 
        'estado_moodle', 
        'estado_academico', 
        'nota_final', 
        'certificado_syric', 
        'fecha_inscripcion'
    )
    list_filter = ('estado_pago', 'estado_moodle', 'estado_academico', 'certificado_syric', 'curso', 'fecha_inscripcion')
    search_fields = (
        'cursante__dni', 
        'cursante__apellido', 
        'cursante__nombre', 
        'curso__nombre', 
        'id_preinscripcion_syric', 
        'comprobante_pago'
    )
    date_hierarchy = 'fecha_inscripcion'
    ordering = ('-fecha_inscripcion',)
    fieldsets = (
        ('Relación de Inscripción', {
            'fields': ('cursante', 'curso', 'id_preinscripcion_syric', 'fecha_inscripcion')
        }),
        ('Estados de Pago y Cursada', {
            'fields': ('estado_pago', 'fecha_pago', 'comprobante_pago', 'estado_moodle', 'estado_academico', 'nota_final')
        }),
        ('Certificación y Extras', {
            'fields': ('certificado_syric', 'observaciones')
        }),
    )
