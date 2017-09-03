# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 22:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_lesson_self_education'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ['number']},
        ),
        migrations.AlterModelOptions(
            name='troop',
            options={'ordering': ['code']},
        ),
        migrations.RemoveField(
            model_name='discipline',
            name='specialties',
        ),
        migrations.AddField(
            model_name='theme',
            name='specialties',
            field=models.ManyToManyField(related_name='themes', to='schedule.Specialty'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='previous_themes',
            field=models.ManyToManyField(related_name='themes', to='schedule.Theme'),
        ),
    ]
