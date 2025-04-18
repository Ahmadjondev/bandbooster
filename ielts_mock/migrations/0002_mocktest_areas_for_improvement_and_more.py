# Generated by Django 4.2.20 on 2025-04-16 17:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ielts_mock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mocktest',
            name='areas_for_improvement',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mocktest',
            name='improvement_plan',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mocktest',
            name='listening_analysis',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mocktest',
            name='reading_analysis',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mocktest',
            name='speaking_analysis',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mocktest',
            name='strengths',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mocktest',
            name='writing_analysis',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='TestQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('section_type', models.CharField(choices=[('reading', 'Reading'), ('listening', 'Listening'), ('writing', 'Writing'), ('speaking', 'Speaking')], max_length=20)),
                ('section_number', models.IntegerField()),
                ('question_number', models.IntegerField()),
                ('question_type', models.CharField(choices=[('multiple_choice', 'Multiple Choice'), ('true_false_not_given', 'True/False/Not Given'), ('matching', 'Matching'), ('fill_in_blank', 'Fill in the Blank'), ('short_answer', 'Short Answer'), ('other', 'Other')], max_length=20)),
                ('question_text', models.TextField()),
                ('options', models.JSONField(blank=True, null=True)),
                ('correct_answer', models.TextField()),
                ('user_answer', models.TextField(blank=True, null=True)),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='ielts_mock.mocktest')),
            ],
            options={
                'ordering': ['section_type', 'section_number', 'question_number'],
            },
        ),
        migrations.CreateModel(
            name='ImprovementPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reading_recommendations', models.JSONField(blank=True, null=True)),
                ('listening_recommendations', models.JSONField(blank=True, null=True)),
                ('writing_recommendations', models.JSONField(blank=True, null=True)),
                ('speaking_recommendations', models.JSONField(blank=True, null=True)),
                ('general_recommendations', models.JSONField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='improvement_plans', to='ielts_mock.mocktest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='improvement_plans', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
