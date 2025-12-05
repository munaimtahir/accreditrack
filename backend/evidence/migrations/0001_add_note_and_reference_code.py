# Generated migration to add note and reference_code to Evidence
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evidence', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evidence',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='evidence',
            name='reference_code',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
