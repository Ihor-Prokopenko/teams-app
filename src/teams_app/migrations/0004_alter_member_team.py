# Generated by Django 5.0.1 on 2024-01-16 04:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams_app', '0003_member_first_name_member_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='teams_app.team'),
        ),
    ]