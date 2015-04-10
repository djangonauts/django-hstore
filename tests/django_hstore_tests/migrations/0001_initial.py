# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django_hstore.fields
import django_hstore.virtual


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BadDefaultsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a', django_hstore.fields.DictionaryField(default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultsInline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('d', django_hstore.fields.DictionaryField(default={b'default': b'yes'})),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a', django_hstore.fields.DictionaryField(default={})),
                ('b', django_hstore.fields.DictionaryField(default=None, null=True)),
                ('c', django_hstore.fields.DictionaryField(default={b'x': b'1'})),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField()),
                ('point', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NullableDataBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NullableRefsBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('refs', django_hstore.fields.ReferencesField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NumberedDataBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField()),
                ('number', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ref',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RefsBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('refs', django_hstore.fields.ReferencesField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchemaDataBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField(null=True, editable=False)),
                ('number', django_hstore.virtual.VirtualField(default=0)),
                ('float', django_hstore.virtual.VirtualField(default=1.0)),
                ('boolean', django_hstore.virtual.VirtualField(default=b'')),
                ('boolean_true', django_hstore.virtual.VirtualField(default=True)),
                ('char', django_hstore.virtual.VirtualField(default=b'test')),
                ('text', django_hstore.virtual.VirtualField(default=b'')),
                ('choice', django_hstore.virtual.VirtualField(default=b'choice1')),
                ('choice2', django_hstore.virtual.VirtualField(default=b'')),
                ('date', django_hstore.virtual.VirtualField(default=b'')),
                ('datetime', django_hstore.virtual.VirtualField(default=None)),
                ('decimal', django_hstore.virtual.VirtualField(default=b'')),
                ('email', django_hstore.virtual.VirtualField(default=b'')),
                ('ip', django_hstore.virtual.VirtualField(default=b'')),
                ('url', django_hstore.virtual.VirtualField(default=b'')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UniqueTogetherDataBag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('data', django_hstore.fields.DictionaryField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='uniquetogetherdatabag',
            unique_together=set([('name', 'data')]),
        ),
        migrations.AddField(
            model_name='defaultsinline',
            name='parent',
            field=models.ForeignKey(to='django_hstore_tests.DefaultsModel'),
            preserve_default=True,
        ),
    ]
