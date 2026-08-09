from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='desativado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
