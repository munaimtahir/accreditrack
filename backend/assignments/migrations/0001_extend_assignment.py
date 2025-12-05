# Generated migration to extend Assignment model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0001_initial'),
        ('accounts', '0001_initial'),
        ('proformas', '0002_add_implementation_criteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='assigned_to',
            field=models.ManyToManyField(blank=True, related_name='assignments', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='instructions',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='proforma_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='proformas.proformaitem'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='scope_type',
            field=models.CharField(choices=[('DEPARTMENT', 'Department'), ('SECTION', 'Section'), ('INDICATOR', 'Indicator')], default='DEPARTMENT', max_length=20),
        ),
        migrations.AddField(
            model_name='assignment',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='proformas.proformasection'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='organizations.department'),
        ),
        migrations.RemoveConstraint(
            model_name='assignment',
            name='assignments_proformatemplate_department_unique',
        ),
    ]
