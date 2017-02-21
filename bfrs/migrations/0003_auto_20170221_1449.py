# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-21 06:49
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bfrs', '0002_bushfire_final_snapshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bushfire',
            name='arrival_area',
            field=models.DecimalField(decimal_places=1, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Fire Area at Arrival (ha)'),
        ),
        migrations.AlterField(
            model_name='bushfire',
            name='cause',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bfrs.Cause'),
        ),
        migrations.AlterField(
            model_name='bushfire',
            name='dispatch_pw_date',
            field=models.DateTimeField(verbose_name=b'Dispatch - P&W'),
        ),
        migrations.AlterField(
            model_name='bushfire',
            name='fuel_type',
            field=models.CharField(max_length=64, verbose_name=b'Fuel Type'),
        ),
        migrations.AlterField(
            model_name='bushfire',
            name='other_cause',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name=b'Other Cause'),
        ),
        migrations.AlterField(
            model_name='bushfire',
            name='potential_fire_level',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)]),
        ),
        migrations.AlterField(
            model_name='bushfire',
            name='report_status',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Initial'), (2, b'Initial Authorised'), (3, b'Final Draft'), (4, b'Final Authorised'), (5, b'Review Draft'), (6, b'Reviewed')], default=1, editable=False),
        ),
    ]
