from django.db import models
from django.contrib.auth.models import User

class Curso(models.Model):
    id_syric = models.CharField("ID Syric", max_length=50, null=True, blank=True, unique=True)
    nombre = models.CharField("Nombre del Curso", max_length=255)
    id_cohorte_moodle = models.CharField("ID Cohorte Moodle", max_length=100, null=True, blank=True)
    arancel = models.DecimalField("Arancel", max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inicio = models.DateField("Fecha de Inicio", null=True, blank=True)
    fecha_fin = models.DateField("Fecha de Fin", null=True, blank=True)
    activo = models.BooleanField("Activo", default=True)
    docentes = models.ManyToManyField(User, verbose_name="Docentes", related_name="cursos_docente", blank=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Cursante(models.Model):
    dni = models.CharField("DNI", max_length=20, unique=True, db_index=True)
    nombre = models.CharField("Nombre", max_length=150)
    apellido = models.CharField("Apellido", max_length=150)
    email = models.EmailField("Email", max_length=254, null=True, blank=True)
    telefono = models.CharField("Teléfono", max_length=50, null=True, blank=True)
    fecha_nacimiento = models.DateField("Fecha de Nacimiento", null=True, blank=True)
    titulo_previo = models.TextField("Título Previo", null=True, blank=True)

    class Meta:
        verbose_name = "Cursante"
        verbose_name_plural = "Cursantes"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class TituloCursante(models.Model):
    cursante = models.ForeignKey(Cursante, on_delete=models.CASCADE, verbose_name="Cursante", related_name="titulos")
    codigo = models.CharField("Código de Título", max_length=50, blank=True, null=True)
    nombre = models.CharField("Nombre de Título", max_length=255)
    nivel = models.CharField("Nivel", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Título de Cursante"
        verbose_name_plural = "Títulos de Cursante"
        ordering = ['nombre']

    def __str__(self):
        parts = []
        if self.codigo:
            parts.append(f"[{self.codigo}]")
        parts.append(self.nombre)
        if self.nivel:
            parts.append(f"({self.nivel})")
        return " ".join(parts)



class Inscripcion(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('BECADO_EXENTO', 'Becado / Exento'),
    ]

    ESTADO_MOODLE_CHOICES = [
        ('NO_MATRICULADO', 'No Matriculado'),
        ('MATRICULADO', 'Matriculado'),
        ('MAIL_ENVIADO', 'Mail Enviado'),
    ]

    ESTADO_ACADEMICO_CHOICES = [
        ('CURSANDO', 'Cursando'),
        ('APROBADO', 'Aprobado'),
        ('DESAPROBADO', 'Desaprobado'),
        ('LIBRE', 'Libre'),
    ]

    CERTIFICADO_SYRIC_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('GESTIONADO', 'Gestionado'),
        ('EMITIDO', 'Emitido'),
    ]

    cursante = models.ForeignKey(Cursante, on_delete=models.CASCADE, verbose_name="Cursante", related_name="inscripciones")
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name="Curso", related_name="inscripciones")
    id_preinscripcion_syric = models.CharField("ID Preinscripción Syric", max_length=50, null=True, blank=True)
    estado_pago = models.CharField("Estado de Pago", max_length=20, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE')
    fecha_pago = models.DateField("Fecha de Pago", null=True, blank=True)
    comprobante_pago = models.FileField("Comprobante de Pago", upload_to='comprobantes/', null=True, blank=True)
    estado_moodle = models.CharField("Estado Moodle", max_length=20, choices=ESTADO_MOODLE_CHOICES, default='NO_MATRICULADO')
    estado_academico = models.CharField("Estado Académico", max_length=20, choices=ESTADO_ACADEMICO_CHOICES, default='CURSANDO')
    nota_final = models.DecimalField("Nota Final", max_digits=5, decimal_places=2, null=True, blank=True)
    certificado_syric = models.CharField("Certificado Syric", max_length=20, choices=CERTIFICADO_SYRIC_CHOICES, default='PENDIENTE')
    fecha_inscripcion = models.DateField("Fecha de Inscripción", null=True, blank=True)
    observaciones = models.TextField("Observaciones", null=True, blank=True)

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ['cursante', 'curso']
        ordering = ['-fecha_inscripcion']

    def __str__(self):
        return f"{self.cursante} en {self.curso}"
