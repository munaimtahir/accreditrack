# Generated migration to update AssignmentUpdate model fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0002_add_assignment_update'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignmentupdate',
            name='status',
        ),
        migrations.AddField(
            model_name='assignmentupdate',
            name='status_before',
            field=models.CharField(blank=True, choices=[('NotStarted', 'Not Started'), ('InProgress', 'In Progress'), ('Completed', 'Completed')], max_length=20),
        ),
        migrations.AddField(
            model_name='assignmentupdate',
            name='status_after',
            field=models.CharField(blank=True, choices=[('NotStarted', 'Not Started'), ('InProgress', 'In Progress'), ('Completed', 'Completed')], max_length=20),
        ),
    ]
