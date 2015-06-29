# -*- coding: utf-8 -*-
import datetime

from django import forms
from django.db.models.aggregates import Count
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from django_hstore.forms import SerializedDictionaryFieldWidget

from django_hstore_tests.models import SerializedDataBag, SerializedDataBagNoID


class TestSerializedDictionaryField(TestCase):
    def setUp(self):
        SerializedDataBag.objects.all().delete()

    def _create_bags(self):
        alpha = SerializedDataBag.objects.create(name='alpha', data={'v': 1, 'v2': '3', 'v3': {'a': 1}})
        beta = SerializedDataBag.objects.create(name='beta', data={'v': 2, 'v2': [1, '4', 5, {'f': 6}], 'v3': {'a': 2}})
        return alpha, beta

    def _create_bitfield_bags(self):
        # create dictionaries with bits as dictionary keys (i.e. bag5 = {'b0':'1', 'b2':'1'})
        for i in range(10):
            SerializedDataBag.objects.create(
                name='bag%d' % (i,),
                data=dict(('b%d' % (bit,), '1') for bit in range(4) if (1 << bit) & i)
            )

    def test_hstore_dict(self):
        alpha, beta = self._create_bags()
        self.assertEqual(alpha.data, {'v': 1, 'v2': '3', 'v3': {'a': 1}})
        self.assertEqual(beta.data, {'v': 2, 'v2': [1, '4', 5, {'f': 6}], 'v3': {'a': 2}})

    def test_number(self):
        databag = SerializedDataBag(name='number')
        databag.data['num'] = 1
        self.assertEqual(databag.data['num'], 1)

        databag.save()
        databag = SerializedDataBag.objects.get(name='number')
        self.assertEqual(databag.data['num'], 1)

        databag = SerializedDataBag(name='number', data={'num': 1})
        self.assertEqual(databag.data['num'], 1)

    def test_non_id_pk(self):
        databag = SerializedDataBagNoID(slug='123', name='abc')
        databag.data['num'] = 1
        databag.save()
        SerializedDataBagNoID.objects.get(slug='123')

    def test_create_directly(self):
        SerializedDataBag.objects.create(name='abc', data={'num': 1})
        SerializedDataBagNoID.objects.create(slug='123', name='abc', data={'num': 1})

    def test_full_clean(self):
        databag = SerializedDataBag(name='number')
        databag.data['num'] = 1
        self.assertEqual(databag.data['num'], 1)

        databag.full_clean()
        databag.save()
        databag = SerializedDataBag.objects.get(name='number')
        self.assertEqual(databag.data['num'], 1)

    def test_list(self):
        databag = SerializedDataBag.objects.create(name='list', data={'list': ['a', 'b', 'c']})
        databag = SerializedDataBag.objects.get(name='list')
        self.assertEqual(databag.data['list'], ['a', 'b', 'c'])

    def test_dictionary(self):
        databag = SerializedDataBag.objects.create(name='dict', data={'dict': {'subkey': 'subvalue'}})
        databag = SerializedDataBag.objects.get(name='dict')
        self.assertEqual(databag.data['dict'], {'subkey': 'subvalue'})

        databag.data['dict'] = {'subkey': True, 'list': ['a', 'b', False]}
        databag.save()
        self.assertEqual(databag.data['dict'], {'subkey': True, 'list': ['a', 'b', False]})

    def test_boolean(self):
        databag = SerializedDataBag.objects.create(name='boolean', data={'boolean': True})
        databag = SerializedDataBag.objects.get(name='boolean')
        self.assertEqual(databag.data['boolean'], True)

    def test_empty_instantiation(self):
        bag = SerializedDataBag.objects.create(name='bag')
        self.assertTrue(isinstance(bag.data, dict))
        self.assertEqual(bag.data, {})

    def test_empty_querying(self):
        SerializedDataBag.objects.create(name='bag')
        self.assertTrue(SerializedDataBag.objects.get(data={}))
        self.assertTrue(SerializedDataBag.objects.filter(data={}))
        self.assertTrue(SerializedDataBag.objects.filter(data__contains={}))

    def test_null_values(self):
        null_v = SerializedDataBag.objects.create(name="test", data={"v": None})
        nonnull_v = SerializedDataBag.objects.create(name="test", data={"v": "item"})

        r = SerializedDataBag.objects.filter(data__isnull={"v": True})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], null_v)

        r = SerializedDataBag.objects.filter(data__isnull={"v": False})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], nonnull_v)

    def test_named_querying(self):
        alpha, beta = self._create_bags()
        self.assertEqual(SerializedDataBag.objects.get(name='alpha'), alpha)
        self.assertEqual(SerializedDataBag.objects.filter(name='beta')[0], beta)

    def test_aggregates(self):
        self._create_bitfield_bags()
        self.assertEqual(SerializedDataBag.objects.filter(data__contains={'b0': '1'}).aggregate(Count('id'))['id__count'], 5)
        self.assertEqual(SerializedDataBag.objects.filter(data__contains={'b1': '1'}).aggregate(Count('id'))['id__count'], 4)

    def test_annotations(self):
        self._create_bitfield_bags()
        self.assertEqual(SerializedDataBag.objects.annotate(num_id=Count('id')).filter(num_id=1)[0].num_id, 1)

    def test_nested_filtering(self):
        self._create_bitfield_bags()
        # Test cumulative successive filters for both dictionaries and other fields
        f = SerializedDataBag.objects.all()
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
        SerializedDataBag.objects.create(name='multilang', data=greets)
        self.assertEqual(greets, SerializedDataBag.objects.get(name='multilang').data)

    def test_query_escaping(self):
        me = self

        def readwrite(s):
            # try create and query with potentially illegal characters in the field and dictionary key/value
            o = SerializedDataBag.objects.create(name=s, data={s: s})
            me.assertEqual(o, SerializedDataBag.objects.get(name=s, data={s: s}))
        readwrite('\' select')
        readwrite('% select')
        readwrite('\\\' select')
        readwrite('-- select')
        readwrite('\n select')
        readwrite('\r select')
        readwrite('* select')

    def test_replace_full_dictionary(self):
        SerializedDataBag.objects.create(name='foo', data={'change': 'old value', 'remove': 'baz'})
        replacement = {'change': 'new value', 'added': 'new'}
        SerializedDataBag.objects.filter(name='foo').update(data=replacement)
        self.assertEqual(replacement, SerializedDataBag.objects.get(name='foo').data)

    def test_equivalence_querying(self):
        alpha, beta = self._create_bags()
        for bag in (alpha, beta):
            data = {'v': bag.data['v'], 'v2': bag.data['v2'], 'v3': bag.data['v3']}
            self.assertEqual(SerializedDataBag.objects.get(data=data), bag)
            r = SerializedDataBag.objects.filter(data=data)
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)

    def test_key_value_subset_querying(self):
        alpha, beta = self._create_bags()
        for bag in (alpha, beta):
            r = SerializedDataBag.objects.filter(data__contains={'v': bag.data['v']})
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)
            r = SerializedDataBag.objects.filter(data__contains={'v': bag.data['v'], 'v2': bag.data['v2']})
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], bag)

    def test_key_value_gt_querying(self):
        alpha, beta = self._create_bags()
        self.assertGreater(beta.data['v'], alpha.data['v'])
        r = SerializedDataBag.objects.filter(data__gt={'v': alpha.data['v']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], beta)
        r = SerializedDataBag.objects.filter(data__gte={'v': alpha.data['v']})
        self.assertEqual(len(r), 2)

    def test_key_value_gt_casting_number_query(self):
        alpha = SerializedDataBag.objects.create(name='alpha', data={'v': 10})
        SerializedDataBag.objects.create(name='alpha', data={'v': 1})

        r = SerializedDataBag.objects.filter(data__gt={'v': 2})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)

    def test_key_value_contains_casting_date_query(self):
        date = datetime.date(2014, 9, 28)
        alpha = SerializedDataBag.objects.create(name='alpha', data={'v': date.isoformat()})

        r = SerializedDataBag.objects.filter(data__contains={'v': date})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)

    def test_multiple_key_value_gt_querying(self):
        alpha, beta = self._create_bags()
        self.assertGreater(beta.data['v'], alpha.data['v'])
        r = SerializedDataBag.objects.filter(data__gt={'v': alpha.data['v'], 'v3': alpha.data['v3']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], beta)
        r = SerializedDataBag.objects.filter(data__gt={'v': alpha.data['v'], 'v3': beta.data['v3']})
        self.assertEqual(len(r), 0)
        r = SerializedDataBag.objects.filter(data__gte={'v': alpha.data['v'], 'v3': alpha.data['v3']})
        self.assertEqual(len(r), 2)
        r = SerializedDataBag.objects.filter(data__gte={'v': alpha.data['v'], 'v3': beta.data['v3']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], beta)

    def test_multiple_key_value_lt_querying(self):
        alpha, beta = self._create_bags()
        self.assertGreater(beta.data['v'], alpha.data['v'])
        r = SerializedDataBag.objects.filter(data__lt={'v': beta.data['v'], 'v3': beta.data['v3']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)
        r = SerializedDataBag.objects.filter(data__lt={'v': beta.data['v'], 'v3': alpha.data['v3']})
        self.assertEqual(len(r), 0)
        r = SerializedDataBag.objects.filter(data__lte={'v': beta.data['v'], 'v3': beta.data['v3']})
        self.assertEqual(len(r), 2)
        r = SerializedDataBag.objects.filter(data__lte={'v': beta.data['v'], 'v3': alpha.data['v3']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)

    def test_key_value_lt_querying(self):
        alpha, beta = self._create_bags()
        self.assertLess(alpha.data['v'], beta.data['v'])
        r = SerializedDataBag.objects.filter(data__lt={'v': beta.data['v']})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], alpha)
        r = SerializedDataBag.objects.filter(data__lte={'v': beta.data['v']})
        self.assertEqual(len(r), 2)

    def test_multiple_key_subset_querying(self):
        alpha, beta = self._create_bags()
        for keys in (['v'], ['v', 'v2']):
            self.assertEqual(SerializedDataBag.objects.filter(data__contains=keys).count(), 2)
        for keys in (['v', 'nv'], ['n1', 'n2']):
            self.assertEqual(SerializedDataBag.objects.filter(data__contains=keys).count(), 0)

    def test_single_key_querying(self):
        alpha, beta = self._create_bags()
        for key in ('v', 'v2'):
            self.assertEqual(SerializedDataBag.objects.filter(data__contains=[key]).count(), 2)
        for key in ('n1', 'n2'):
            self.assertEqual(SerializedDataBag.objects.filter(data__contains=[key]).count(), 0)

    def test_simple_text_icontains_querying(self):
        alpha, beta = self._create_bags()
        SerializedDataBag.objects.create(name='gamma', data={'theKey': 'someverySpecialValue', 'v2': '3'})

        self.assertEqual(SerializedDataBag.objects.filter(data__contains='very').count(), 1)
        self.assertEqual(SerializedDataBag.objects.filter(data__contains='very')[0].name, 'gamma')
        self.assertEqual(SerializedDataBag.objects.filter(data__icontains='specialvalue').count(), 1)
        self.assertEqual(SerializedDataBag.objects.filter(data__icontains='specialvalue')[0].name, 'gamma')

        self.assertEqual(SerializedDataBag.objects.filter(data__contains='the').count(), 1)
        self.assertEqual(SerializedDataBag.objects.filter(data__contains='the')[0].name, 'gamma')
        self.assertEqual(SerializedDataBag.objects.filter(data__icontains='eke').count(), 1)
        self.assertEqual(SerializedDataBag.objects.filter(data__icontains='eke')[0].name, 'gamma')

    def test_containment_lookup(self):
        alpha, beta = self._create_bags()

        qs = SerializedDataBag.objects.filter(data__contains=1)
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0], alpha)
        self.assertEqual(qs[1], beta)

        qs = SerializedDataBag.objects.filter(data__icontains=2)
        self.assertEqual(len(qs), 2)
        self.assertEqual(list(qs), [alpha, beta])

        qs = SerializedDataBag.objects.filter(data__contains='3')
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0], alpha)
        self.assertEqual(qs[1], beta)

        qs = SerializedDataBag.objects.filter(data__contains='4')
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], beta)

        # Multiple filters
        qs = SerializedDataBag.objects.filter(data__contains='4').filter(data__contains=5)
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], beta)

        qs = SerializedDataBag.objects.filter(data__contains=1).filter(data__contains='4')
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], beta)

        # Contains value in nested dict
        qs = SerializedDataBag.objects.filter(data__contains=6)
        self.assertEqual(len(qs), 1)

    def test_invalid_comparison_lookup_values(self):
        alpha, beta = self._create_bags()
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__lt=[1, 2])[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__lt=99)[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__lte=[1, 2])[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__lte=99)[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__gt=[1, 2])[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__gt=99)[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__gte=[1, 2])[0]
        with self.assertRaises(ValueError):
            SerializedDataBag.objects.filter(data__gte=99)[0]

    def test_hkeys(self):
        alpha, beta = self._create_bags()
        self.assertEqual(SerializedDataBag.objects.hkeys(id=alpha.id, attr='data'), ['v', 'v2', 'v3'])
        self.assertEqual(SerializedDataBag.objects.hkeys(id=beta.id, attr='data'), ['v', 'v2', 'v3'])

    def test_hpeek(self):
        alpha, beta = self._create_bags()
        self.assertEqual(SerializedDataBag.objects.hpeek(id=alpha.id, attr='data', key='v'), 1)
        self.assertEqual(SerializedDataBag.objects.filter(id=alpha.id).hpeek(attr='data', key='v'), 1)
        self.assertEqual(SerializedDataBag.objects.hpeek(id=alpha.id, attr='data', key='invalid'), None)

    def test_hremove(self):
        alpha, beta = self._create_bags()
        self.assertEqual(SerializedDataBag.objects.get(name='alpha').data, alpha.data)
        SerializedDataBag.objects.filter(name='alpha').hremove('data', 'v2')
        self.assertEqual(SerializedDataBag.objects.get(name='alpha').data, {'v': 1, 'v3': {'a': 1}})

        self.assertEqual(SerializedDataBag.objects.get(name='beta').data, beta.data)
        SerializedDataBag.objects.filter(name='beta').hremove('data', ['v', 'v2', 'v3'])
        self.assertEqual(SerializedDataBag.objects.get(name='beta').data, {})

    def test_hslice(self):
        alpha, beta = self._create_bags()
        self.assertEqual(SerializedDataBag.objects.hslice(id=alpha.id, attr='data', keys=['v']), {'v': 1})
        self.assertEqual(SerializedDataBag.objects.filter(id=alpha.id).hslice(attr='data', keys=['v']), {'v': 1})
        self.assertEqual(SerializedDataBag.objects.hslice(id=alpha.id, attr='data', keys=['ggg']), {})

    def test_hupdate(self):
        alpha, beta = self._create_bags()
        self.assertEqual(SerializedDataBag.objects.get(name='alpha').data, alpha.data)
        SerializedDataBag.objects.filter(name='alpha').hupdate('data', {'v2': '10', 'v3': {'a': '20'}})
        self.assertEqual(SerializedDataBag.objects.get(name='alpha').data, {'v': 1, 'v2': '10', 'v3': {'a': '20'}})

    def test_hstore_model_field_validation(self):
        d = SerializedDataBag()
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
            'd': {'test': 'test'}
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
        url = reverse('admin:django_hstore_tests_serializeddatabag_change', args=[alpha.id])
        response = self.client.get(url)
        # ensure textarea with id="id_data" is there
        self.assertContains(response, 'textarea')
        self.assertContains(response, 'id_data')

    def test_dictionary_default_admin_widget(self):
        class HForm(forms.ModelForm):
            class Meta:
                model = SerializedDataBag
                exclude = []

        form = HForm()
        self.assertEqual(form.fields['data'].widget.__class__, SerializedDictionaryFieldWidget)

    def test_dictionary_custom_admin_widget(self):
        class CustomWidget(forms.Widget):
            pass

        class HForm(forms.ModelForm):
            class Meta:
                model = SerializedDataBag
                widgets = {'data': CustomWidget}
                exclude = []

        form = HForm()
        self.assertEqual(form.fields['data'].widget.__class__, CustomWidget)

    def test_properties_hstore(self):
        """
        Make sure the hstore field does what it is supposed to.
        """
        instance = SerializedDataBag()
        test_props = {'foo': 'bar', 'size': '3'}

        instance.name = "foo"
        instance.data = test_props
        instance.save()

        self.assertIsInstance(instance.data, dict)
        self.assertEqual(instance.data, test_props)
        instance = SerializedDataBag.objects.get(pk=instance.pk)

        self.assertIsInstance(instance.data, dict)

        self.assertEqual(instance.data, test_props)
        self.assertEqual(instance.data['size'], '3')
        self.assertIn('foo', instance.data)

    def test_unicode(self):
        i = SerializedDataBag()
        i.data['key'] = 'è'
        i.save()

        i.data['key'] = u'è'
        i.save()

    def test_str(self):
        d = SerializedDataBag()
        self.assertEqual(str(d.data), '{}')
