# Generated by Django 3.2.25 on 2025-04-17 06:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ielts_mock', '0005_delete_writingpractice'),
    ]

    operations = [
        migrations.CreateModel(
            name='WritingPractice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('task_type', models.CharField(choices=[('task1', 'Task 1 - Report'), ('task2', 'Task 2 - Essay')], max_length=10)),
                ('prompt', models.TextField()),
                ('response', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('task_achievement', models.FloatField(blank=True, null=True)),
                ('coherence_cohesion', models.FloatField(blank=True, null=True)),
                ('lexical_resource', models.FloatField(blank=True, null=True)),
                ('grammatical_range', models.FloatField(blank=True, null=True)),
                ('overall_score', models.FloatField(blank=True, null=True)),
                ('feedback', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writing_practices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
