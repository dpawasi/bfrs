# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-24 06:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bfrs', '0021_auto_20170324_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bushfire',
            name='fire_level',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3)], null=True),
        ),
    ]
