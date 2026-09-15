from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academico', '0002_alter_cursante_titulo_previo_titulocursante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscripcion',
            name='estado_pago',
            field=models.CharField(
                choices=[
                    ('PENDIENTE', 'Pendiente'),
                    ('PAGADO', 'Pagado'),
                    ('PARCIALMENTE_COBRADO', 'Parcialmente Cobrado'),
                    ('BECADO_EXENTO', 'Becado / Exento'),
                ],
                default='PENDIENTE',
                max_length=20,
                verbose_name='Estado de Pago',
            ),
        ),
    ]
