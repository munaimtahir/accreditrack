# Generated migration to add module FK to ProformaTemplate
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proformas', '0001_initial'),
        ('modules', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proformatemplate',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='templates', to='modules.module'),
        ),
    ]
