# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields
import django_hstore.virtual


class Migration(migrations.Migration):

    dependencies = [
        ('django_hstore_tests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NullSchemaDataBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField(default=None, null=True, editable=False)),
                ('number', django_hstore.virtual.VirtualField(default=0)),
                ('char', django_hstore.virtual.VirtualField(default=b'test')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
