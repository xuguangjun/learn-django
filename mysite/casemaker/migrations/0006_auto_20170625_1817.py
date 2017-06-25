# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-25 10:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casemaker', '0005_remove_case_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='config_id',
            field=models.IntegerField(default=1, unique=True),
        ),
        migrations.AlterField(
            model_name='naviversion',
            name='version_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]