# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-03 03:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bfrs', '0023_auto_20170803_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='bushfire',
            name='sss_id',
            field=models.CharField(default=1, max_length=64, verbose_name=b'Unique SSS ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bushfiresnapshot',
            name='sss_id',
            field=models.CharField(default=1, max_length=64, verbose_name=b'Unique SSS ID'),
            preserve_default=False,
        ),
    ]
