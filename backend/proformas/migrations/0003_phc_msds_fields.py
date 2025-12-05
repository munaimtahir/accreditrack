# Migration to add PHC MSDS fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proformas', '0002_add_implementation_criteria'),
    ]

    operations = [
        # Add code field to ProformaTemplate
        migrations.AddField(
            model_name='proformatemplate',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        # Add parent and section_type to ProformaSection
        migrations.AddField(
            model_name='proformasection',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='proformas.proformasection'),
        ),
        migrations.AddField(
            model_name='proformasection',
            name='section_type',
            field=models.CharField(choices=[('CATEGORY', 'Category'), ('STANDARD', 'Standard')], default='STANDARD', max_length=20),
        ),
        # Add scoring fields to ProformaItem
        migrations.AddField(
            model_name='proformaitem',
            name='max_score',
            field=models.SmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='proformaitem',
            name='weightage_percent',
            field=models.SmallIntegerField(default=100),
        ),
        migrations.AddField(
            model_name='proformaitem',
            name='is_licensing_critical',
            field=models.BooleanField(default=False),
        ),
    ]
