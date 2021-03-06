# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-03 09:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_auto_20170731_2218'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherTheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternative', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='audience',
            name='themes',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='themes',
        ),
        migrations.AddField(
            model_name='theme',
            name='audiences',
            field=models.ManyToManyField(related_name='themes', to='schedule.Audience'),
        ),
        migrations.AddField(
            model_name='teachertheme',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Teacher'),
        ),
        migrations.AddField(
            model_name='teachertheme',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Theme'),
        ),
        migrations.AddField(
            model_name='theme',
            name='teachers',
            field=models.ManyToManyField(related_name='themes', through='schedule.TeacherTheme', to='schedule.Teacher'),
        ),
    ]
