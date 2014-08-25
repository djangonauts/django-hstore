# -*- coding: utf-8 -*-
import sys
import json
import pickle
from decimal import Decimal

import django

from django.db import transaction
from django.db import connection
from django.db.models.aggregates import Count
from django.db.utils import IntegrityError, DatabaseError
from django import forms, get_version as get_django_version
from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.test import TestCase
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.utils.encoding import force_text

from django_hstore import get_version, hstore
from django_hstore.forms import DictionaryFieldWidget, ReferencesFieldWidget
from django_hstore.fields import HStoreDict
from django_hstore.exceptions import HStoreDictException
from django_hstore.utils import unserialize_references, serialize_references, acquire_reference
from django_hstore.virtual import create_hstore_virtual_field

from django_hstore_tests.models import *


class TestDictionaryField(TestCase):
    def setUp(self):
        DataBag.objects.all().delete()
        Ref.objects.all().delete()
        RefsBag.objects.all().delete()

    def _create_bags(self):
        alpha = DataBag.objects.create(name='alpha', data={'v': '1', 'v2': '3'})
        beta = DataBag.objects.create(name='beta', data={'v': '2', 'v2': '4'})
        return alpha, beta

    def _create_bitfield_bags(self):
        # create dictionaries with bits as dictionary keys (i.e. bag5 = { 'b0':'1', 'b2':'1'})
        for i in range(10):
            DataBag.objects.create(name='bag%d' % (i,),
                                   data=dict(('b%d' % (bit,), '1') for bit in range(4) if (1 << bit) & i))

    def test_hstore_dict(self):
        alpha, beta = self._create_bags()
        self.assertEqual(alpha.data, {'v': '1', 'v2': '3'})
        self.assertEqual(beta.data, {'v': '2', 'v2': '4'})

    def test_decimal(self):
        databag = DataBag(name='decimal')
        databag.data['dec'] = Decimal('1.01')
        self.assertEqual(databag.data['dec'], force_text(Decimal('1.01')))

        databag.save()
        databag = DataBag.objects.get(name='decimal')
        self.assertEqual(databag.data['dec'], force_text(Decimal('1.01')))

        databag = DataBag(name='decimal', data={'dec': Decimal('1.01')})
        self.assertEqual(databag.data['dec'], force_text(Decimal('1.01')))
    
    def test_long(self):
        if sys.version < '3':
            l = long(100000000000)
            databag = DataBag(name='long')
            databag.data['long'] = l
            self.assertEqual(databag.data['long'], force_text(l))
    
            databag.save()
            databag = DataBag.objects.get(name='long')
            self.assertEqual(databag.data['long'], force_text(l))
    
            databag = DataBag(name='long', data={'long': l})
            self.assertEqual(databag.data['long'], force_text(l))

    def test_number(self):
        databag = DataBag(name='number')
        databag.data['num'] = 1
        self.assertEqual(databag.data['num'], '1')

        databag.save()
        databag = DataBag.objects.get(name='number')
        self.assertEqual(databag.data['num'], '1')

        databag = DataBag(name='number', data={ 'num': 1 })
        self.assertEqual(databag.data['num'], '1')

    def test_list(self):
        databag = DataBag.objects.create(name='list', data={ 'list': ['a', 'b', 'c'] })
        databag = DataBag.objects.get(name='list')
        self.assertEqual(json.loads(databag.data['list']), ['a', 'b', 'c'])

    def test_dictionary(self):
        databag = DataBag.objects.create(name='dict', data={ 'dict': {'subkey': 'subvalue'} })
        databag = DataBag.objects.get(name='dict')
        self.assertEqual(json.loads(databag.data['dict']), {'subkey': 'subvalue'})

        databag.data['dict'] = {'subkey': True, 'list': ['a', 'b', False]}
        databag.save()
        self.assertEqual(json.loads(databag.data['dict']), {'subkey': True, 'list': ['a', 'b', False]})

    def test_boolean(self):
        databag = DataBag.objects.create(name='boolean', data={ 'boolean': True })
        databag = DataBag.objects.get(name='boolean')
        self.assertEqual(json.loads(databag.data['boolean']), True)

    def test_is_pickable(self):
        m = DefaultsModel()
        m.save()
        try:
            pickle.dumps(m)
        except TypeError as e:
            self.fail('pickle of DefaultsModel failed: %s' % e)

    def test_empty_instantiation(self):
        bag = DataBag.objects.create(name='bag')
        self.assertTrue(isinstance(bag.data, dict))
        self.assertEqual(bag.data, {})

    def test_empty_querying(self):
        DataBag.objects.create(name='bag')
        self.assertTrue(DataBag.objects.get(data={}))
        self.assertTrue(DataBag.objects.filter(data={}))
        self.assertTrue(DataBag.objects.filter(data__contains={}))

    def test_nullable_queryinig(self):
        NullableDataBag.objects.create(name='nullable')
        self.assertTrue(NullableDataBag.objects.get(data=None))
        self.assertTrue(NullableDataBag.objects.filter(data__exact=None))
        self.assertTrue(NullableDataBag.objects.filter(data__isnull=True))
        self.assertFalse(NullableDataBag.objects.filter(data__isnull=False))

    def test_named_querying(self):
        alpha, beta = self._create_bags()
        self.assertEqual(DataBag.objects.get(name='alpha'), alpha)
        self.assertEqual(DataBag.objects.filter(name='beta')[0], beta)

    def test_aggregates(self):
        self._create_bitfield_bags()

        self.assertEqual(DataBag.objects.filter(data__contains={'b0': '1'}).aggregate(Count('id'))['id__count'], 5)
        self.assertEqual(DataBag.objects.filter(data__contains={'b1': '1'}).aggregate(Count('id'))['id__count'], 4)

    def test_annotations(self):
        self._create_bitfield_bags()

        self.assertEqual(DataBag.objects.annotate(num_id=Count('id')).filter(num_id=1)[0].num_id, 1)

    def test_nested_filtering(self):
        self._create_bitfield_bags()

        # Test cumulative successive filters for both dictionaries and other fields
        f = DataBag.objects.all()
        self.assertEqual(10, f.count())
        f = f.filter(data__contains={'b0': '1'})
        self.assertEqual(5, f.count())
        f = f.filter(data__contains={'b1': '1'})
        self.assertEqual(2, f.count())
        f = f.filter(name='bag3')
        self.assertEqual(1, f.count())

    def test_unicode_processing(self):
        greets = {
            u'de': u'Gr\xfc\xdfe, Welt',
            u'en': u'hello, world',
            u'es': u'hola, ma\xf1ana',
            u'he': u'\u05e9\u05dc\u05d5\u05dd, \u05e2\u05d5\u05dc\u05dd',
            u'jp': u'\u3053\u3093\u306b\u3061\u306f\u3001\u4e16\u754c',
            u'zh': u'\u4f60\u597d\uff0c\u4e16\u754c',
        }
        DataBag.objects.create(name='multilang', data=greets)
        self.assertEqual(greets, DataBag.objects.get(name='multilang').data)

    def test_query_escaping(self):
        me = self

        def readwrite(s):
            # try create and query with potentially illegal characters in the field and dictionary key/value
            o = DataBag.objects.create(name=s, data={s: s})
            me.assertEqual(o, DataBag.objects.get(name=s, data={s: s}))
        readwrite('\' select')
        readwrite('% select')
        readwrite('\\\' select')
        readwrite('-- select')
        readwrite('\n select')
        readwrite('\r select')
        readwrite('* select')

    def test_replace_full_dictionary(self):
        DataBag.objects.create(name='foo', data={'change': 'old value', 'remove': 'baz'})

        replacement = {'change': 'new value', 'added': 'new'}
        DataBag.objects.filter(name='foo').update(data=replacement)
        self.assertEqual(replacement, DataBag.objects.get(name='foo').data)

    def test_equivalence_querying(self):
        alpha, beta = self._create_bags()
        for bag in (alpha, beta):
            data = {'v': bag.data['v'], 'v2': bag.data['v2']}
            self.assertEqual(DataBag.objects.get(data=data), bag)
            r = DataBag.objects.filter(data=data)
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)

    def test_key_value_subset_querying(self):
        alpha, beta = self._create_bags()
        for bag in (alpha, beta):
            r = DataBag.objects.filter(data__contains={'v': bag.data['v']})
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)
            r = DataBag.objects.filter(data__contains={'v': bag.data['v'], 'v2': bag.data['v2']})
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)

    def test_value_in_subset_querying(self):
        alpha, beta = self._create_bags()
        res = DataBag.objects.filter(data__contains={'v': [alpha.data['v']]})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], alpha)
        res = DataBag.objects.filter(data__contains={'v': [alpha.data['v'], beta.data['v']]})
        self.assertEqual(len(res), 2)
        self.assertEqual(set(res), set([alpha, beta]))

        # int values are ok
        r = DataBag.objects.filter(data__contains={'v': [int(alpha.data['v'])]})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)

    def test_key_value_gt_querying(self):
        alpha, beta = self._create_bags()
        self.assertGreater(beta.data['v'], alpha.data['v'])
        r = DataBag.objects.filter(data__gt={'v': alpha.data['v']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], beta)
        r = DataBag.objects.filter(data__gte={'v': alpha.data['v']})
        self.assertEqual(len(r), 2)

    def test_multiple_key_value_gt_querying(self):
        alpha, beta = self._create_bags()
        self.assertGreater(beta.data['v'], alpha.data['v'])
        r = DataBag.objects.filter(data__gt={'v': alpha.data['v'], 'v2': alpha.data['v2']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], beta)
        r = DataBag.objects.filter(data__gt={'v': alpha.data['v'], 'v2': beta.data['v2']})
        self.assertEqual(len(r), 0)
        r = DataBag.objects.filter(data__gte={'v': alpha.data['v'], 'v2': alpha.data['v2']})
        self.assertEqual(len(r), 2)
        r = DataBag.objects.filter(data__gte={'v': alpha.data['v'], 'v2': beta.data['v2']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], beta)

    def test_multiple_key_value_lt_querying(self):
        alpha, beta = self._create_bags()
        self.assertGreater(beta.data['v'], alpha.data['v'])
        r = DataBag.objects.filter(data__lt={'v': beta.data['v'], 'v2': beta.data['v2']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)
        r = DataBag.objects.filter(data__lt={'v': beta.data['v'], 'v2': alpha.data['v2']})
        self.assertEqual(len(r), 0)
        r = DataBag.objects.filter(data__lte={'v': beta.data['v'], 'v2': beta.data['v2']})
        self.assertEqual(len(r), 2)
        r = DataBag.objects.filter(data__lte={'v': beta.data['v'], 'v2': alpha.data['v2']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)

    def test_key_value_lt_querying(self):
        alpha, beta = self._create_bags()
        self.assertLess(alpha.data['v'], beta.data['v'])
        r = DataBag.objects.filter(data__lt={'v': beta.data['v']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)
        r = DataBag.objects.filter(data__lte={'v': beta.data['v']})
        self.assertEqual(len(r), 2)

    def test_multiple_key_subset_querying(self):
        alpha, beta = self._create_bags()
        for keys in (['v'], ['v', 'v2']):
            self.assertEqual(DataBag.objects.filter(data__contains=keys).count(), 2)
        for keys in (['v', 'nv'], ['n1', 'n2']):
            self.assertEqual(DataBag.objects.filter(data__contains=keys).count(), 0)

    def test_single_key_querying(self):
        alpha, beta = self._create_bags()
        for key in ('v', 'v2'):
            self.assertEqual(DataBag.objects.filter(data__contains=[key]).count(), 2)
        for key in ('n1', 'n2'):
            self.assertEqual(DataBag.objects.filter(data__contains=[key]).count(), 0)

    def test_simple_text_icontains_querying(self):
        alpha, beta = self._create_bags()
        gamma = DataBag.objects.create(name='gamma', data={'theKey': 'someverySpecialValue', 'v2': '3'})

        self.assertEqual(DataBag.objects.filter(data__contains='very').count(), 1)
        self.assertEqual(DataBag.objects.filter(data__contains='very')[0].name, 'gamma')
        self.assertEqual(DataBag.objects.filter(data__icontains='specialvalue').count(), 1)
        self.assertEqual(DataBag.objects.filter(data__icontains='specialvalue')[0].name, 'gamma')

        self.assertEqual(DataBag.objects.filter(data__contains='the').count(), 1)
        self.assertEqual(DataBag.objects.filter(data__contains='the')[0].name, 'gamma')
        self.assertEqual(DataBag.objects.filter(data__icontains='eke').count(), 1)
        self.assertEqual(DataBag.objects.filter(data__icontains='eke')[0].name, 'gamma')

    def test_invalid_containment_lookup_values(self):
        alpha, beta = self._create_bags()
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__contains=99)[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__icontains=99)[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__icontains=[])[0]

    def test_invalid_comparison_lookup_values(self):
        alpha, beta = self._create_bags()
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__lt=[1,2])[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__lt=99)[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__lte=[1,2])[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__lte=99)[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__gt=[1,2])[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__gt=99)[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__gte=[1,2])[0]
        with self.assertRaises(ValueError):
            DataBag.objects.filter(data__gte=99)[0]

    def test_hkeys(self):
        alpha, beta = self._create_bags()
        self.assertEqual(DataBag.objects.hkeys(id=alpha.id, attr='data'), ['v', 'v2'])
        self.assertEqual(DataBag.objects.hkeys(id=beta.id, attr='data'), ['v', 'v2'])

    def test_hpeek(self):
        alpha, beta = self._create_bags()
        self.assertEqual(DataBag.objects.hpeek(id=alpha.id, attr='data', key='v'), '1')
        self.assertEqual(DataBag.objects.filter(id=alpha.id).hpeek(attr='data', key='v'), '1')
        self.assertEqual(DataBag.objects.hpeek(id=alpha.id, attr='data', key='invalid'), None)

    def test_hremove(self):
        alpha, beta = self._create_bags()
        self.assertEqual(DataBag.objects.get(name='alpha').data, alpha.data)
        DataBag.objects.filter(name='alpha').hremove('data', 'v2')
        self.assertEqual(DataBag.objects.get(name='alpha').data, {'v': '1'})

        self.assertEqual(DataBag.objects.get(name='beta').data, beta.data)
        DataBag.objects.filter(name='beta').hremove('data', ['v', 'v2'])
        self.assertEqual(DataBag.objects.get(name='beta').data, {})

    def test_hslice(self):
        alpha, beta = self._create_bags()
        self.assertEqual(DataBag.objects.hslice(id=alpha.id, attr='data', keys=['v']), {'v': '1'})
        self.assertEqual(DataBag.objects.filter(id=alpha.id).hslice(attr='data', keys=['v']), {'v': '1'})
        self.assertEqual(DataBag.objects.hslice(id=alpha.id, attr='data', keys=['ggg']), {})

    def test_hupdate(self):
        alpha, beta = self._create_bags()
        self.assertEqual(DataBag.objects.get(name='alpha').data, alpha.data)
        DataBag.objects.filter(name='alpha').hupdate('data', {'v2': '10', 'v3': '20'})
        self.assertEqual(DataBag.objects.get(name='alpha').data, {'v': '1', 'v2': '10', 'v3': '20'})

    def test_default(self):
        m = DefaultsModel()
        m.save()

    def test_bad_default(self):
        m = BadDefaultsModel()
        try:
            m.save()
        except IntegrityError:
            transaction.rollback()
        else:
            self.assertTrue(False)

    def test_serialization_deserialization(self):
        alpha, beta = self._create_bags()
        self.assertEqual(json.loads(str(DataBag.objects.get(name='alpha').data)), json.loads(str(alpha.data)))
        self.assertEqual(json.loads(str(DataBag.objects.get(name='beta').data)), json.loads(str(beta.data)))

    def test_hstoredictionaryexception(self):
        # ok
        HStoreDict({})

        # json object string allowed
        HStoreDict('{}')

        # None is ok, will be converted to empty dict
        HStoreDict(None)
        HStoreDict()

        # non-json string not allowed
        with self.assertRaises(HStoreDictException):
            HStoreDict('wrong')

        # list not allowed
        with self.assertRaises(HStoreDictException):
            HStoreDict(['wrong'])

        # json array string representation not allowed
        with self.assertRaises(HStoreDictException):
            HStoreDict('["wrong"]')

        # number not allowed
        with self.assertRaises(HStoreDictException):
            HStoreDict(3)

    def test_hstoredictionary_unicoce_vs_str(self):
        d = HStoreDict({ 'test': 'test' })
        self.assertEqual(d.__str__(), d.__unicode__())

    def test_hstore_model_field_validation(self):
        d = DataBag()

        with self.assertRaises(ValidationError):
            d.full_clean()

        d.data = 'test'

        with self.assertRaises(ValidationError):
            d.full_clean()

        d.data = '["test"]'

        with self.assertRaises(ValidationError):
            d.full_clean()

        d.data = ["test"]

        with self.assertRaises(ValidationError):
            d.full_clean()

        d.data = {
            'a': 1,
            'b': 2.2,
            'c': ['a', 'b'],
            'd': { 'test': 'test' }
        }

        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_admin_widget(self):
        alpha, beta = self._create_bags()

        # create admin user
        admin = User.objects.create(username='admin', password='tester', is_staff=True, is_superuser=True, is_active=True)
        admin.set_password('tester')
        admin.save()
        # login as admin
        self.client.login(username='admin', password='tester')

        # access admin change form page
        url = reverse('admin:django_hstore_tests_databag_change', args=[alpha.id])
        response = self.client.get(url)
        # ensure textarea with id="id_data" is there
        self.assertContains(response, 'textarea')
        self.assertContains(response, 'id_data')

    def test_dictionary_default_admin_widget(self):
        class HForm(forms.ModelForm):
            class Meta:
                model = DataBag
                exclude = []

        form = HForm()
        self.assertEqual(form.fields['data'].widget.__class__, DictionaryFieldWidget)

    def test_dictionary_custom_admin_widget(self):
        class CustomWidget(forms.Widget):
            pass

        class HForm(forms.ModelForm):
            class Meta:
                model = DataBag
                widgets = {'data': CustomWidget}
                exclude = []

        form = HForm()
        self.assertEqual(form.fields['data'].widget.__class__, CustomWidget)

    def test_references_default_admin_widget(self):
        class HForm(forms.ModelForm):
            class Meta:
                model = RefsBag
                exclude = []

        form = HForm()
        self.assertEqual(form.fields['refs'].widget.__class__, ReferencesFieldWidget)

    def test_references_custom_admin_widget(self):
        class CustomWidget(forms.Widget):
            pass

        class HForm(forms.ModelForm):
            class Meta:
                model = RefsBag
                widgets = {'refs': CustomWidget}
                exclude = []

        form = HForm()
        self.assertEqual(form.fields['refs'].widget.__class__, CustomWidget)

    def test_get_version(self):
        get_version()

    def test_unique_together(self):
        d = UniqueTogetherDataBag()
        d.name = 'test'
        d.data = { 'test': 'test '}
        d.full_clean()
        d.save()

        d = UniqueTogetherDataBag()
        d.name = 'test'
        d.data = { 'test': 'test '}
        with self.assertRaises(ValidationError):
            d.full_clean()
    
    def test_properties_hstore(self):
        """
        Make sure the hstore field does what it is supposed to.
        """
        from django_hstore.fields import HStoreDict

        instance = DataBag()
        test_props = {'foo':'bar', 'size': '3'}

        instance.name = "foo"
        instance.data = test_props
        instance.save()

        self.assertEqual(type(instance.data), HStoreDict)
        self.assertEqual(instance.data, test_props)
        instance = DataBag.objects.get(pk=instance.pk)

        self.assertEqual(type(instance.data), HStoreDict)

        self.assertEqual(instance.data, test_props)
        self.assertEqual(instance.data['size'], '3')
        self.assertIn('foo', instance.data)
    
    def test_unicode(self):
        i = DataBag()
        i.data['key'] = 'è'
        i.save()
        
        i.data['key'] = u'è'
        i.save()
    
    def test_get_default(self):
        d = HStoreDict()
        self.assertIsNone(d.get('none_key', None))
        self.assertIsNone(d.get('none_key'))


class SchemaTests(TestCase):
    if get_django_version()[0:3] >= '1.6':
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
            
            response = self.client.post(url, { 'name': 'test_add', 'number': 3, 'float': 2.4 })
            d = SchemaDataBag.objects.all()[0]
            self.assertEqual(d.name, 'test_add')
            self.assertEqual(d.number, 3)
            self.assertEqual(d.float, 2.4)
        
        def test_admin_add_utf8(self):
            self._login_as_admin()
            url = reverse('admin:django_hstore_tests_schemadatabag_add')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            
            response = self.client.post(url, { 'name': 'test_add', 'number': 3, 'float': 2.4, 'char': 'è' })
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
            
            response = self.client.post(url, { 'name': 'test_change', 'number': 6, 'float': 2.6 })
            d = SchemaDataBag.objects.get(pk=d.id)
            self.assertEqual(d.name, 'test_change')
            self.assertEqual(d.number, 6)
            self.assertEqual(d.data['number'], 6)
            self.assertEqual(d.float, 2.6)
            self.assertEqual(d.data['float'], 2.6)
        
        def test_create_hstore_virtual_field(self):
            integer = create_hstore_virtual_field('IntegerField', { 'default': 0 }, 'data')
            self.assertIsInstance(integer, models.IntegerField)
            char = create_hstore_virtual_field('CharField', { 'default': 'test', 'blank': True, 'max_length': 10 }, 'data')
            self.assertIsInstance(char, models.CharField)
            text = create_hstore_virtual_field('TextField', { 'blank': True }, 'data')
            self.assertIsInstance(text, models.TextField)
        
        def test_create_hstore_virtual_field_wrong_class(self):
            with self.assertRaises(ValueError):
                create_hstore_virtual_field(float, { 'blank': True }, 'data')
        
        def test_create_hstore_virtual_field_wrong_class_string(self):
            with self.assertRaises(ValueError):
                create_hstore_virtual_field('IdoNotExist', { 'blank': True }, 'data')
        
        def test_create_hstore_virtual_field_concrete_class(self):
            integer = create_hstore_virtual_field(models.IntegerField, { 'default': 0 }, 'data')
            url = create_hstore_virtual_field(models.URLField, { 'blank': True }, 'data')
            self.assertTrue(isinstance(integer, models.IntegerField))
            self.assertTrue(isinstance(url, models.URLField))
        
        def test_DictionaryField_with_schema(self):
            data = hstore.DictionaryField(schema=[
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
                data = hstore.DictionaryField(schema='')
                
            with self.assertRaises(ValueError):
                data = hstore.DictionaryField(schema='WRONG')
        
        def test_schema_validation_wrong_list(self):
            with self.assertRaises(ValueError):
                data = hstore.DictionaryField(schema=[])
            
            with self.assertRaises(ValueError):
                data = hstore.DictionaryField(schema=['i am teasing you'])
        
        def test_schema_validation_wrong_dict(self):
            with self.assertRaises(ValueError):
                data = hstore.DictionaryField(schema=[
                    { 'wrong': 'wrong' }
                ])
            
            with self.assertRaises(ValueError):
                data = hstore.DictionaryField(schema=[
                    { 'name': 'test' }
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
        
    else:
        def test_improperly_configured(self):            
            with self.assertRaises(ImproperlyConfigured):
                class SchemaDataBag(models.Model):
                    name = models.CharField(max_length=32)
                    data = hstore.DictionaryField(schema=[
                        {
                            'name': 'number',
                            'class': 'IntegerField',
                            'kwargs': {
                                'default': 0
                            }
                        }
                    ])


class NotTransactionalTests(SimpleTestCase):
    if django.VERSION[:2] >= (1,6):
        def test_hstore_registring_in_transaction_block(self):
            obj1 = DataBag.objects.create(name='alpha1', data={'v': '1', 'v2': '3'})
            obj2 = DataBag.objects.create(name='alpha2', data={'v': '1', 'v2': '3'})

            # Close any existing connection previously do anything
            connection.close()

            with transaction.atomic():
                qs = DataBag.objects.filter(name__in=["alpha2", "alpha1"])
                self.assertIsInstance(qs[0].data, HStoreDict)

            obj1.delete()
            obj2.delete()

            connection.close()
    else:
        def test_hstore_registring_in_transaction_block(self):
            obj1 = DataBag.objects.create(name='alpha1', data={'v': '1', 'v2': '3'})
            obj2 = DataBag.objects.create(name='alpha2', data={'v': '1', 'v2': '3'})

            # Close any existing connection previously do anything
            connection.close()

            with transaction.commit_on_success():
                qs = DataBag.objects.filter(name__in=["alpha2", "alpha1"])
                self.assertIsInstance(qs[0].data, HStoreDict)

            obj1.delete()
            obj2.delete()

            connection.close()


class TestReferencesField(TestCase):
    def setUp(self):
        Ref.objects.all().delete()
        RefsBag.objects.all().delete()

    def _create_bags(self):
        refs = [Ref.objects.create(name=str(i)) for i in range(4)]
        alpha = RefsBag.objects.create(name='alpha', refs={'0': refs[0], '1': refs[1]})
        beta = RefsBag.objects.create(name='beta', refs={'0': refs[2], '1': refs[3]})
        return alpha, beta, refs

    def test_empty_instantiation(self):
        bag = RefsBag.objects.create(name='bag')
        self.assertTrue(isinstance(bag.refs, dict))
        self.assertEqual(bag.refs, {})

    def test_unsaved_empty_instantiation(self):
        bag = RefsBag(name='bag')
        self.assertEqual(bag.refs.get('idontexist', 'default'), 'default')
        self.assertTrue(isinstance(bag.refs, dict))

    def test_unsave_empty_instantiation_of_nullable_ref(self):
        bag = NullableRefsBag(name='bag')
        self.assertEqual(bag.refs.get('idontexist', 'default'), 'default')
        self.assertTrue(isinstance(bag.refs, dict))

    def test_simple_retrieval(self):
        alpha, beta, refs = self._create_bags()
        alpha = RefsBag.objects.get(name='alpha')
        self.assertEqual(Ref.objects.get(name='0'), alpha.refs['0'])

    def test_simple_retrieval_get(self):
        alpha, beta, refs = self._create_bags()
        alpha = RefsBag.objects.get(name='alpha')
        self.assertEqual(Ref.objects.get(name='0'), alpha.refs.get('0'))

        # try getting a non existent key
        self.assertEqual(alpha.refs.get('idontexist', 'default'), 'default')
        self.assertEqual(alpha.refs.get('idontexist'), None)

    def test_empty_querying(self):
        RefsBag.objects.create(name='bag')
        self.assertTrue(RefsBag.objects.get(refs={}))
        self.assertTrue(RefsBag.objects.filter(refs={}))
        self.assertTrue(RefsBag.objects.filter(refs__contains={}))

    def test_equivalence_querying(self):
        alpha, beta, refs = self._create_bags()
        for bag in (alpha, beta):
            refs = {'0': bag.refs['0'], '1': bag.refs['1']}
            self.assertEqual(RefsBag.objects.get(refs=refs), bag)
            r = RefsBag.objects.filter(refs=refs)
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)

    def test_key_value_subset_querying(self):
        alpha, beta, refs = self._create_bags()
        for bag in (alpha, beta):
            r = RefsBag.objects.filter(refs__contains={'0': bag.refs['0']})
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)
            r = RefsBag.objects.filter(refs__contains={'0': bag.refs['0'], '1': bag.refs['1']})
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)

    def test_multiple_key_subset_querying(self):
        alpha, beta, refs = self._create_bags()
        for keys in (['0'], ['0', '1']):
            self.assertEqual(RefsBag.objects.filter(refs__contains=keys).count(), 2)
        for keys in (['0', 'nv'], ['n1', 'n2']):
            self.assertEqual(RefsBag.objects.filter(refs__contains=keys).count(), 0)

    def test_single_key_querying(self):
        alpha, beta, refs = self._create_bags()
        for key in ('0', '1'):
            self.assertEqual(RefsBag.objects.filter(refs__contains=[key]).count(), 2)
        for key in ('n1', 'n2'):
            self.assertEqual(RefsBag.objects.filter(refs__contains=[key]).count(), 0)

    def test_hkeys(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.hkeys(id=alpha.id, attr='refs'), ['0', '1'])

    def test_hpeek(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.hpeek(id=alpha.id, attr='refs', key='0'), refs[0])
        self.assertEqual(RefsBag.objects.filter(id=alpha.id).hpeek(attr='refs', key='0'), refs[0])
        self.assertEqual(RefsBag.objects.hpeek(id=alpha.id, attr='refs', key='invalid'), None)

    def test_hremove(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.get(name='alpha').refs['0'], alpha.refs['0'])
        self.assertEqual(RefsBag.objects.get(name='alpha').refs['1'], alpha.refs['1'])
        self.assertIn("0", RefsBag.objects.get(name='alpha').refs)
        RefsBag.objects.filter(name='alpha').hremove('refs', '0')
        self.assertNotIn("0", RefsBag.objects.get(name='alpha').refs)
        self.assertIn("1", RefsBag.objects.get(name='alpha').refs)

        self.assertEqual(RefsBag.objects.get(name='beta').refs['0'], beta.refs['0'])
        self.assertEqual(RefsBag.objects.get(name='beta').refs['1'], beta.refs['1'])
        RefsBag.objects.filter(name='beta').hremove('refs', ['0', '1'])
        self.assertEqual(RefsBag.objects.get(name='beta').refs, {})

    def test_hslice(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.hslice(id=alpha.id, attr='refs', keys=['0']), {'0': refs[0]})
        self.assertEqual(RefsBag.objects.filter(id=alpha.id).hslice(attr='refs', keys=['0']), {'0': refs[0]})
        self.assertEqual(RefsBag.objects.hslice(id=alpha.id, attr='refs', keys=['invalid']), {})

    def test_admin_reference_field(self):
        alpha, beta, refs = self._create_bags()

        # create admin user
        admin = User.objects.create(username='admin', password='tester', is_staff=True, is_superuser=True, is_active=True)
        admin.set_password('tester')
        admin.save()
        # login as admin
        self.client.login(username='admin', password='tester')

        # access admin change form page
        url = reverse('admin:django_hstore_tests_refsbag_change', args=[alpha.id])
        response = self.client.get(url)
        # ensure textarea with id="id_data" is there
        self.assertContains(response, 'textarea')
        self.assertContains(response, 'id_refs')

    def test_unserialize_references_edge_cases(self):
        alpha, beta, refs = self._create_bags()

        refs = unserialize_references(alpha.refs)
        # repeat
        refs = unserialize_references(alpha.refs)
        self.assertEqual(len(unserialize_references(refs).keys()), 2)
        self.assertEqual(unserialize_references(None), {})

    def test_serialize_references_edge_cases(self):
        self.assertEqual(serialize_references(None), {})
        self.assertEqual(serialize_references({ 'test': 'test' }), { 'test': 'test' })

    def test_acquire_references_edge_cases(self):
        with self.assertRaises(ValueError):
            acquire_reference(None)
        with self.assertRaises(ValueError):
            acquire_reference(None)

    def test_native_contains(self):
        d = DataBag()
        d.name = "A bag of data"
        d.data = {
            'd1': '1',
            'd2': '2'
        }
        d.save()
        result = DataBag.objects.filter(name__contains='of data')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = DataBag.objects.filter(name__contains='OF data')
        self.assertEqual(result.count(), 0)

    def test_native_icontains(self):
        d = DataBag()
        d.name = "A bag of data"
        d.data = {
            'd1': '1',
            'd2': '2'
        }
        d.save()
        result = DataBag.objects.filter(name__icontains='A bAg')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)

    def test_native_gt(self):
        d = NumberedDataBag()
        d.name = "A bag of data"
        d.number = 12
        d.save()
        result = NumberedDataBag.objects.filter(number__gt=12)
        self.assertEqual(result.count(), 0)
        result = NumberedDataBag.objects.filter(number__gt=1)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = NumberedDataBag.objects.filter(number__gt=13)
        self.assertEqual(result.count(), 0)

    def test_native_gte(self):
        d = NumberedDataBag()
        d.name = "A bag of data"
        d.number = 12
        d.save()
        result = NumberedDataBag.objects.filter(number__gte=12)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = NumberedDataBag.objects.filter(number__gte=1)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = NumberedDataBag.objects.filter(number__gte=13)
        self.assertEqual(result.count(), 0)

    def test_native_lt(self):
        d = NumberedDataBag()
        d.name = "A bag of data"
        d.number = 12
        d.save()
        result = NumberedDataBag.objects.filter(number__lt=20)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = NumberedDataBag.objects.filter(number__lt=12)
        self.assertEqual(result.count(), 0)
        result = NumberedDataBag.objects.filter(number__lt=1)
        self.assertEqual(result.count(), 0)

    def test_native_lte(self):
        d = NumberedDataBag()
        d.name = "A bag of data"
        d.number = 12
        d.save()
        result = NumberedDataBag.objects.filter(number__lte=12)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = NumberedDataBag.objects.filter(number__lte=13)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0].pk, d.pk)
        result = NumberedDataBag.objects.filter(number__lte=1)
        self.assertEqual(result.count(), 0)


if GEODJANGO:
    from django.contrib.gis.geos import GEOSGeometry

    class TestDictionaryFieldPlusGIS(TestCase):
        """ Test DictionaryField with gis backend """

        def setUp(self):
            Location.objects.all().delete()

        pnt1 = GEOSGeometry('POINT(65.5758316 57.1345383)')
        pnt2 = GEOSGeometry('POINT(65.2316 57.3423233)')

        def _create_locations(self):
            loc1 = Location.objects.create(name='Location1', data={'prop1': '1', 'prop2': 'test_value'}, point=self.pnt1)
            loc2 = Location.objects.create(name='Location2', data={'prop1': '2', 'prop2': 'test_value'}, point=self.pnt2)
            return loc1, loc2

        def test_location_create(self):
            l1, l2 = self._create_locations()
            other_loc = Location.objects.get(point__contains=self.pnt1)
            self.assertEqual(other_loc.data, {'prop1': '1', 'prop2': 'test_value'})

        def test_location_hupdate(self):
            l1, l2 = self._create_locations()
            Location.objects.filter(point__contains=self.pnt1).hupdate('data', {'prop1': '2'})
            loc = Location.objects.exclude(point__contains=self.pnt2)[0]
            self.assertEqual(loc.data, {'prop1': '2', 'prop2': 'test_value'})
            loc = Location.objects.get(point__contains=self.pnt2)
            self.assertNotEqual(loc.data, {'prop1': '1', 'prop2': 'test_value'})

        def test_location_contains(self):
            l1, l2 = self._create_locations()
            self.assertEqual(Location.objects.filter(data__contains={'prop1': '1'}).count(), 1)
            self.assertEqual(Location.objects.filter(data__contains={'prop1': '2'}).count(), 1)

        def test_location_geomanager(self):
            l1, l2 = self._create_locations()
            d1 = Location.objects.filter(point__distance_lte=(self.pnt1, 70000))
            self.assertEqual(d1.count(), 2)


    class TestReferencesFieldPlusGIS(TestDictionaryFieldPlusGIS):
        """ Test ReferenceField with gis backend """

        def _create_locations(self):
            loc1 = Location.objects.create(name='Location1', data={'prop1': '1', 'prop2': 'test_value'}, point=self.pnt1)
            loc2 = Location.objects.create(name='Location2', data={'prop1': '2', 'prop2': 'test_value'}, point=self.pnt2)
            return loc1, loc2

        def test_location_create(self):
            l1, l2 = self._create_locations()
            loc_1 = Location.objects.get(point__contains=self.pnt1)
            self.assertEqual(loc_1.data, {'prop1': '1', 'prop2': 'test_value'})
            loc_2 = Location.objects.get(point__contains=self.pnt2)
            self.assertEqual(loc_2.data, {'prop1': '2', 'prop2': 'test_value'})

        def test_location_hupdate(self):
            l1, l2 = self._create_locations()
            Location.objects.filter(point__contains=self.pnt1).hupdate('data', {'prop1': '2'})
            loc = Location.objects.exclude(point__contains=self.pnt2)[0]
            self.assertEqual(loc.data, {'prop1': '2', 'prop2': 'test_value'})
            loc = Location.objects.get(point__contains=self.pnt2)
            self.assertNotEqual(loc.data, {'prop1': '1', 'prop2': 'test_value'})
