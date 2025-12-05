# Generated migration for modules app
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'modules',
                'ordering': ['display_name'],
            },
        ),
        migrations.CreateModel(
            name='UserModuleRole',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(choices=[('SUPERADMIN', 'Super Admin'), ('DASHBOARD_ADMIN', 'Dashboard Admin'), ('CATEGORY_ADMIN', 'Category Admin'), ('USER', 'User')], max_length=20)),
                ('categories', models.JSONField(blank=True, default=list)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to='modules.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_roles', to='accounts.user')),
            ],
            options={
                'db_table': 'user_module_roles',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'module')},
            },
        ),
    ]
