# -*- coding: utf-8 -*-
import os
import sys
import shutil

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

from django import VERSION as DJANGO_VERSION
from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import TestCase

from django_hstore import hstore
from django_hstore.virtual import create_hstore_virtual_field

from django_hstore_tests.models import SchemaDataBag, NullSchemaDataBag


MIGRATION_PATH = '{0}/../{1}'.format(os.path.dirname(__file__), 'migrations')


class TestSchemaMode(TestCase):
    @classmethod
    def tearDownClass(cls):
        TestSchemaMode._delete_migrations()

    @classmethod
    def _delete_migrations(cls):
        # delete migration files
        try:
            shutil.rmtree(MIGRATION_PATH)
        except OSError:
            pass

    def _login_as_admin(self):
        # create admin user
        admin = User.objects.create(username='admin', password='tester', is_staff=True, is_superuser=True, is_active=True)
        admin.set_password('tester')
        admin.save()
        # login as admin
        self.client.login(username='admin', password='tester')

    def test_to_python_conversion(self):
        d = SchemaDataBag().data
        d['number'] = 2
        self.assertEqual(d['number'], 2)
        d['boolean'] = True
        self.assertTrue(d['boolean'])
        d['boolean'] = False
        self.assertFalse(d['boolean'])
        d['float'] = 2.5
        self.assertEqual(d['float'], 2.5)
        self.assertEqual(d.get('float'), 2.5)

    def test_dict_get(self):
        d = SchemaDataBag().data
        d['number'] = 2
        self.assertEqual(d.get('number'), 2)
        self.assertEqual(d.get('default_test', 'default'), 'default')
        self.assertIsNone(d.get('default_test'))

    def test_virtual_field_default_value(self):
        d = SchemaDataBag()
        self.assertEqual(d.number, 0)
        self.assertEqual(d.float, 1.0)
        # accessing the HStoreDict key raises KeyError if not assigned previously
        with self.assertRaises(KeyError):
            d.data['number']

    def test_virtual_field_called_statically(self):
        with self.assertRaises(AttributeError):
            SchemaDataBag.number

    def test_schemadatabag_assignment(self):
        d = SchemaDataBag()
        d.number = 4
        self.assertEqual(d.data['number'], 4)
        d.float = 2.5
        self.assertEqual(d.data['float'], 2.5)
        d.data['number'] = 5
        self.assertEqual(d.number, 5)

    def test_schemadatabag_save(self):
        d = SchemaDataBag()
        d.name = 'test'
        d.number = 4
        d.float = 2.0
        d.save()
        d = SchemaDataBag.objects.get(pk=d.id)
        self.assertEqual(d.number, 4)
        self.assertEqual(d.data['number'], 4)

    def test_schemadatabag_validation_error(self):
        d = SchemaDataBag()
        d.name = 'test'
        d.number = 'WRONG'
        d.float = 2.0

        with self.assertRaises(ValidationError):
            d.full_clean()

        d.number = 9
        d.float = 'WRONG'
        with self.assertRaises(ValidationError):
            d.full_clean()

        d.float = 2.0
        d.char = 'test'
        d.choice = 'choice1'
        d.full_clean()
        d.save()

    def test_admin_list(self):
        self._login_as_admin()
        url = reverse('admin:django_hstore_tests_schemadatabag_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_add(self):
        self._login_as_admin()
        url = reverse('admin:django_hstore_tests_schemadatabag_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'name': 'test_add', 'number': 3, 'float': 2.4})
        d = SchemaDataBag.objects.all()[0]
        self.assertEqual(d.name, 'test_add')
        self.assertEqual(d.number, 3)
        self.assertEqual(d.float, 2.4)

    def test_admin_add_utf8(self):
        self._login_as_admin()
        url = reverse('admin:django_hstore_tests_schemadatabag_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'name': 'test_add', 'number': 3, 'float': 2.4, 'char': 'è'})
        d = SchemaDataBag.objects.all()[0]
        self.assertEqual(d.name, 'test_add')
        self.assertEqual(d.number, 3)
        self.assertEqual(d.float, 2.4)

    def test_admin_change(self):
        self._login_as_admin()
        d = SchemaDataBag()
        d.name = 'test1'
        d.number = 1
        d.float = 2.5
        d.save()
        url = reverse('admin:django_hstore_tests_schemadatabag_change', args=[d.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'name': 'test_change', 'number': 6, 'float': 2.6})
        d = SchemaDataBag.objects.get(pk=d.id)
        self.assertEqual(d.name, 'test_change')
        self.assertEqual(d.number, 6)
        self.assertEqual(d.data['number'], 6)
        self.assertEqual(d.float, 2.6)
        self.assertEqual(d.data['float'], 2.6)

    def test_create_hstore_virtual_field(self):
        integer = create_hstore_virtual_field('IntegerField', {'default': 0}, 'data')
        self.assertIsInstance(integer, models.IntegerField)
        char = create_hstore_virtual_field('CharField', {'default': 'test', 'blank': True, 'max_length': 10}, 'data')
        self.assertIsInstance(char, models.CharField)
        text = create_hstore_virtual_field('TextField', {'blank': True}, 'data')
        self.assertIsInstance(text, models.TextField)

    def test_create_hstore_virtual_field_wrong_class(self):
        with self.assertRaises(ValueError):
            create_hstore_virtual_field(float, {'blank': True}, 'data')

    def test_create_hstore_virtual_field_wrong_class_string(self):
        with self.assertRaises(ValueError):
            create_hstore_virtual_field('IdoNotExist', {'blank': True}, 'data')

    def test_create_hstore_virtual_field_concrete_class(self):
        integer = create_hstore_virtual_field(models.IntegerField, {'default': 0}, 'data')
        url = create_hstore_virtual_field(models.URLField, {'blank': True}, 'data')
        self.assertTrue(isinstance(integer, models.IntegerField))
        self.assertTrue(isinstance(url, models.URLField))

    def test_DictionaryField_with_schema(self):
        hstore.DictionaryField(schema=[
            {
                'name': 'number',
                'class': 'IntegerField',
                'kwargs': {
                    'default': 0,
                    'verbose_name': 'verbose number'
                }
            }
        ])

    def test_schema_validation_string(self):
        with self.assertRaises(ValueError):
            hstore.DictionaryField(schema='')

        with self.assertRaises(ValueError):
            hstore.DictionaryField(schema='WRONG')

    def test_schema_validation_wrong_list(self):
        with self.assertRaises(ValueError):
            hstore.DictionaryField(schema=[])

        with self.assertRaises(ValueError):
            hstore.DictionaryField(schema=['i am teasing you'])

    def test_schema_validation_wrong_dict(self):
        with self.assertRaises(ValueError):
            hstore.DictionaryField(schema=[
                {'wrong': 'wrong'}
            ])

        with self.assertRaises(ValueError):
            hstore.DictionaryField(schema=[
                {'name': 'test'}
            ])

    def test_utf8(self):
        d = SchemaDataBag()
        d.name = 'test'
        d.number = 4
        d.float = 2.0
        d.char = 'è'
        d.full_clean()
        d.save()

        d = SchemaDataBag.objects.get(pk=d.id)
        self.assertEqual(d.char, u'è')

        d.char = u'è'
        d.full_clean()
        d.save()

        d = SchemaDataBag.objects.get(pk=d.id)
        self.assertEqual(d.char, u'è')

    def test_create(self):
        s1 = SchemaDataBag.objects.create(
            name='create1',
            number=2,
            float=2.2,
            boolean=True,
            boolean_true=False,
            choice='choice2',
            choice2='choice1',
            char='create2',
            text='create3'
        )
        s1 = SchemaDataBag.objects.get(pk=s1.pk)
        self.assertEqual(s1.name, 'create1')
        self.assertEqual(s1.number, 2)
        self.assertEqual(s1.float, 2.2)
        self.assertEqual(s1.boolean, True)
        self.assertEqual(s1.boolean_true, False)
        self.assertEqual(s1.choice, 'choice2')
        self.assertEqual(s1.choice2, 'choice1')
        self.assertEqual(s1.char, 'create2')
        self.assertEqual(s1.text, 'create3')

    def test_extra_key_regression(self):
        s = SchemaDataBag()
        s.data['extrakey'] = 2
        self.assertEqual(s.data['extrakey'], '2')

    def test_virtual_date_drf_support(self):
        class FakeModel(object):
            date = '2014-08-08'

        virtual_date = SchemaDataBag()._hstore_virtual_fields['date']

        self.assertEqual(virtual_date.value_to_string(FakeModel()), '2014-08-08')

    def test_basefield_attribute(self):
        virtual_field = SchemaDataBag()._hstore_virtual_fields['char']
        self.assertEqual(virtual_field.__basefield__.__name__, 'CharField')

    def test_str(self):
        d = SchemaDataBag()
        self.assertEqual(str(d.data), '{}')

    if DJANGO_VERSION[:2] >= (1, 8):
        def test_reload_schema(self):
            # cache some stuff
            f = SchemaDataBag._meta.get_field('data')
            original_schema = list(f.schema)
            local_fields_length = len(SchemaDataBag._meta.local_fields)
            hstore_virtual_fields_keys = list(SchemaDataBag._hstore_virtual_fields.keys())

            # original state
            d = SchemaDataBag()
            self.assertTrue(d.data.schema_mode)
            self.assertEqual(len(SchemaDataBag._meta.virtual_fields), len(original_schema))
            self.assertEqual(len(SchemaDataBag._meta.fields), len(original_schema) + local_fields_length)
            self.assertEqual(len(SchemaDataBag._meta.local_fields), 3)
            self.assertTrue(hasattr(SchemaDataBag, '_hstore_virtual_fields'))
            for key in hstore_virtual_fields_keys:
                self.assertTrue(hasattr(d, key))

            # schema erased
            f.reload_schema(None)
            self.assertIsNone(f.schema)
            self.assertFalse(f.schema_mode)
            self.assertTrue(f.editable)
            self.assertEqual(len(SchemaDataBag._meta.virtual_fields), 0)
            self.assertEqual(len(SchemaDataBag._meta.fields), local_fields_length)
            self.assertEqual(len(SchemaDataBag._meta.local_fields), local_fields_length)
            self.assertFalse(hasattr(SchemaDataBag, '_hstore_virtual_fields'))
            d = SchemaDataBag()
            self.assertFalse(d.data.schema_mode)
            for key in hstore_virtual_fields_keys:
                self.assertFalse(hasattr(d, key))

            # reload original schema
            f.reload_schema(original_schema)
            d = SchemaDataBag()
            self.assertTrue(d.data.schema_mode)
            self.assertEqual(len(SchemaDataBag._meta.virtual_fields), len(original_schema))
            self.assertEqual(len(SchemaDataBag._meta.fields), len(original_schema) + local_fields_length)
            self.assertEqual(len(SchemaDataBag._meta.local_fields), 3)
            self.assertTrue(hasattr(SchemaDataBag, '_hstore_virtual_fields'))
            for key in hstore_virtual_fields_keys:
                self.assertTrue(hasattr(d, key))
    else:
        # TODO: will removed when django 1.7 will be deprecated
        def test_reload_schema(self):
            # cache some stuff
            f = SchemaDataBag._meta.get_field('data')
            original_schema = list(f.schema)
            concrete_fields_length = len(SchemaDataBag._meta.concrete_fields)
            hstore_virtual_fields_keys = list(SchemaDataBag._hstore_virtual_fields.keys())

            # original state
            d = SchemaDataBag()
            self.assertTrue(d.data.schema_mode)
            self.assertEqual(len(SchemaDataBag._meta.virtual_fields), len(original_schema))
            self.assertEqual(len(SchemaDataBag._meta.fields), len(original_schema) + concrete_fields_length)
            self.assertEqual(len(SchemaDataBag._meta.local_fields), len(original_schema) + concrete_fields_length)
            self.assertTrue(hasattr(SchemaDataBag, '_hstore_virtual_fields'))
            for key in hstore_virtual_fields_keys:
                self.assertTrue(hasattr(d, key))

            # schema erased
            f.reload_schema(None)
            self.assertIsNone(f.schema)
            self.assertFalse(f.schema_mode)
            self.assertTrue(f.editable)
            self.assertEqual(len(SchemaDataBag._meta.virtual_fields), 0)
            self.assertEqual(len(SchemaDataBag._meta.fields), concrete_fields_length)
            self.assertEqual(len(SchemaDataBag._meta.local_fields), concrete_fields_length)
            self.assertFalse(hasattr(SchemaDataBag, '_hstore_virtual_fields'))
            d = SchemaDataBag()
            self.assertFalse(d.data.schema_mode)
            for key in hstore_virtual_fields_keys:
                self.assertFalse(hasattr(d, key))

            # reload original schema
            f.reload_schema(original_schema)
            d = SchemaDataBag()
            self.assertTrue(d.data.schema_mode)
            self.assertEqual(len(SchemaDataBag._meta.virtual_fields), len(original_schema))
            self.assertEqual(len(SchemaDataBag._meta.fields), len(original_schema) + concrete_fields_length)
            self.assertEqual(len(SchemaDataBag._meta.local_fields), len(original_schema) + concrete_fields_length)
            self.assertTrue(hasattr(SchemaDataBag, '_hstore_virtual_fields'))
            for key in hstore_virtual_fields_keys:
                self.assertTrue(hasattr(d, key))

    def test_datetime_is_none(self):
        """ issue #82 https://github.com/djangonauts/django-hstore/issues/82 """
        d = SchemaDataBag()
        d.name = 'datetime'
        self.assertIsNone(d.datetime, None)
        d.full_clean()
        d.save()
        d = SchemaDataBag.objects.get(name='datetime')
        self.assertIsNone(d.datetime, None)

    def test_none_handling(self):
        """ failing test for https://github.com/djangonauts/django-hstore/pull/92 """
        d = NullSchemaDataBag()
        self.assertIsNone(d.data)
        d.char = 'testing'
        d.number = 2
        self.assertEqual(d.char, 'testing')
        self.assertEqual(d.number, 2)
        d.char = ''
        d.number = 0
        self.assertEqual(d.char, '')
        self.assertEqual(d.number, 0)

    if DJANGO_VERSION[:2] >= (1, 7):
        def _test_migrations_issue_103(self):
            """ failing test for https://github.com/djangonauts/django-hstore/issues/103 """
            # start capturing output
            output = StringIO()
            sys.stdout = output
            call_command('makemigrations', 'django_hstore_tests')
            # stop capturing print statements
            sys.stdout = sys.__stdout__
            self.assertIn('No changes detected', output.getvalue())
            # add a new migration which replicates the bug in #103
            with open('{0}/{1}'.format(MIGRATION_PATH, '0002_issue_103.py'), 'w') as f:
                f.write("""# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
import datetime
import django_hstore.virtual
class Migration(migrations.Migration):
    dependencies = [
        ('django_hstore_tests', '0001_initial'),
    ]
    operations = [
        migrations.AlterField(
            model_name='schemadatabag',
            name='datetime',
            field=django_hstore.virtual.VirtualField(default=datetime.datetime(2015, 4, 19, 16, 44, 9, 417872)),
            preserve_default=True,
        ),
    ]""")
                f.close()
            # start capturing output
            output = StringIO()
            sys.stdout = output
            call_command('migrate', 'django_hstore_tests', fake_initial=True)
            # stop capturing print statements
            sys.stdout = sys.__stdout__
            self.assertIn('Applying django_hstore_tests.0002_issue_103... OK', output.getvalue())

        def _test_migrations_issue_117(self):
            """ failing test for https://github.com/djangonauts/django-hstore/issues/117 """
            # start capturing output
            output = StringIO()
            sys.stdout = output
            call_command('makemigrations', 'django_hstore_tests')
            # stop capturing print statements
            sys.stdout = sys.__stdout__
            self.assertIn('0001_initial', output.getvalue())
            # start capturing output
            output = StringIO()
            sys.stdout = output
            call_command('makemigrations', 'django_hstore_tests')
            # stop capturing print statements
            sys.stdout = sys.__stdout__
            self.assertIn('No changes detected', output.getvalue())

        def test_migrations(self):
            self._test_migrations_issue_117()
            # changes in django 1.8 make this test obsolete
            if DJANGO_VERSION[:2] == (1, 7):
                self._test_migrations_issue_103()
            TestSchemaMode._delete_migrations()
