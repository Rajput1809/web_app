# Generated by Django 5.1.4 on 2024-12-21 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0003_rename_engineer_complaint_assigned_engineer_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='complaint',
            old_name='photo',
            new_name='image',
        ),
    ]
