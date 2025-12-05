# Generated migration to add implementation_criteria to ProformaItem
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proformas', '0001_add_module_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='proformaitem',
            name='implementation_criteria',
            field=models.TextField(blank=True),
        ),
    ]
