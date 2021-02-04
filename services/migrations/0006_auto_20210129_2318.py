# Generated by Django 3.1.5 on 2021-01-29 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_category_icon_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='QuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(max_length=200)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.question')),
            ],
            options={
                'db_table': 'question_choices',
            },
        ),
        migrations.CreateModel(
            name='SelectedChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.questionchoice')),
            ],
            options={
                'db_table': 'selected_choices',
            },
        ),
        migrations.DeleteModel(
            name='LessonStyle',
        ),
        migrations.RemoveField(
            model_name='request',
            name='age',
        ),
        migrations.RemoveField(
            model_name='request',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='request',
            name='lesson_date',
        ),
        migrations.RemoveField(
            model_name='request',
            name='lesson_style',
        ),
        migrations.RemoveField(
            model_name='request',
            name='lesson_type',
        ),
        migrations.RemoveField(
            model_name='request',
            name='master_gender',
        ),
        migrations.RemoveField(
            model_name='request',
            name='preferred_lesson_day',
        ),
        migrations.AddField(
            model_name='request',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.service'),
        ),
        migrations.DeleteModel(
            name='LessonType',
        ),
        migrations.AddField(
            model_name='selectedchoice',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.request'),
        ),
    ]