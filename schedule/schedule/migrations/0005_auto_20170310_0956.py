# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-10 09:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20170310_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='date_of',
            field=models.DateField(),
        ),
    ]
