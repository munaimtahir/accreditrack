# Generated migration to add AssignmentUpdate model
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0001_extend_assignment'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentUpdate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('NotStarted', 'Not Started'), ('InProgress', 'In Progress'), ('Completed', 'Completed')], max_length=20, null=True)),
                ('note', models.TextField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='assignments.assignment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_updates', to='accounts.user')),
            ],
            options={
                'db_table': 'assignment_updates',
                'ordering': ['-created_at'],
            },
        ),
    ]
