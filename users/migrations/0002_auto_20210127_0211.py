# Generated by Django 3.1.5 on 2021-01-27 02:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='master',
            old_name='master_payment',
            new_name='master_payments',
        ),
        migrations.RenameField(
            model_name='master',
            old_name='master_region',
            new_name='master_regions',
        ),
        migrations.RenameField(
            model_name='master',
            old_name='review',
            new_name='reviews',
        ),
    ]