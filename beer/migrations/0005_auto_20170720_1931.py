# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-20 17:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beer', '0004_breweries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breweries',
            name='is_organic',
            field=models.CharField(max_length=1),
        ),
    ]
