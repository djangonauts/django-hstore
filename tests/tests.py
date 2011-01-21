import unittest
from .app.models import DataBag, Ref, RefsBag

class TestCase(unittest.TestCase):
    def setUp(self):
        DataBag.objects.all().delete()
        Ref.objects.all().delete()
        RefsBag.objects.all().delete()

class TestDictionaryField(TestCase):
    def _create_bags(self):
        alpha = DataBag.objects.create(name='alpha', data={'v': '1', 'v2': '3'})
        beta = DataBag.objects.create(name='beta', data={'v': '2', 'v2': '4'})
        return alpha, beta

    def test_empty_instantiation(self):
        bag = DataBag.objects.create(name='bag')
        self.assertTrue(isinstance(bag.data, dict))
        self.assertEqual(bag.data, {})

    def test_empty_querying(self):
        bag = DataBag.objects.create(name='bag')
        self.assertTrue(DataBag.objects.get(data={}))
        self.assertTrue(DataBag.objects.filter(data={}))
        self.assertTrue(DataBag.objects.filter(data__contains={}))

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

    def test_multiple_key_subset_querying(self):
        alpha, beta = self._create_bags()
        for keys in (['v'], ['v', 'v2']):
            self.assertEqual(DataBag.objects.filter(data__contains=keys).count(), 2)
        for keys in (['v', 'nv'], ['n1', 'n2']):
            self.assertEqual(DataBag.objects.filter(data__contains=keys).count(), 0)

    def test_single_key_querying(self):
        alpha, beta = self._create_bags()
        for key in ('v', 'v2'):
            self.assertEqual(DataBag.objects.filter(data__contains=key).count(), 2)
        for key in ('n1', 'n2'):
            self.assertEqual(DataBag.objects.filter(data__contains=key).count(), 0)

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

class TestReferencesField(TestCase):
    def _create_bags(self):
        refs = [Ref.objects.create(name=str(i)) for i in range(4)]
        alpha = RefsBag.objects.create(name='alpha', refs={'0': refs[0], '1': refs[1]})
        beta = RefsBag.objects.create(name='beta', refs={'0': refs[2], '1': refs[3]})
        return alpha, beta, refs

    def test_empty_instantiation(self):
        bag = RefsBag.objects.create(name='bag')
        self.assertTrue(isinstance(bag.refs, dict))
        self.assertEqual(bag.refs, {})

    def test_empty_querying(self):
        bag = RefsBag.objects.create(name='bag')
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
            self.assertEqual(RefsBag.objects.filter(refs__contains=key).count(), 2)
        for key in ('n1', 'n2'):
            self.assertEqual(RefsBag.objects.filter(refs__contains=key).count(), 0)

    def test_hkeys(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.hkeys(id=alpha.id, attr='refs'), ['0', '1'])

    def test_hpeek(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.hpeek(id=alpha.id, attr='refs', key='0'), refs[0])
        self.assertEqual(RefsBag.objects.filter(id=alpha.id).hpeek(attr='refs', key='0'), refs[0])
        self.assertEqual(RefsBag.objects.hpeek(id=alpha.id, attr='refs', key='invalid'), None)

    def test_hslice(self):
        alpha, beta, refs = self._create_bags()
        self.assertEqual(RefsBag.objects.hslice(id=alpha.id, attr='refs', keys=['0']), {'0': refs[0]})
        self.assertEqual(RefsBag.objects.filter(id=alpha.id).hslice(attr='refs', keys=['0']), {'0': refs[0]})
        self.assertEqual(RefsBag.objects.hslice(id=alpha.id, attr='refs', keys=['invalid']), {})
