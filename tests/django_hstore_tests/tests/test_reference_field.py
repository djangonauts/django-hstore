from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django import forms

from django_hstore.forms import ReferencesFieldWidget
from django_hstore.utils import unserialize_references, serialize_references, acquire_reference

from django_hstore_tests.models import Ref, RefsBag, NullableRefsBag


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

    def test_unserialize_references(self):
        alpha, beta, refs = self._create_bags()
        ref = dict(alpha=alpha, beta=beta)
        serialized_refs = serialize_references(ref)
        unserialized_refs = unserialize_references(serialized_refs)
        self.assertEqual(unserialized_refs['alpha'].pk, alpha.pk)
        self.assertEqual(unserialized_refs['beta'].pk, beta.pk)

    def test_serialize_references_edge_cases(self):
        self.assertEqual(serialize_references(None), {})
        self.assertEqual(serialize_references({'test': 'test'}), {'test': 'test'})

    def test_acquire_references_value_error(self):
        with self.assertRaises(ValueError):
            acquire_reference(None)
        with self.assertRaises(ValueError):
            acquire_reference('')

    def test_acquire_references_none(self):
        self.assertIsNone(acquire_reference('django_hstore_tests.models.SchemaDataBag:2'))

    def test_str(self):
        r = RefsBag()
        self.assertEqual(str(r.refs), '{}')

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
