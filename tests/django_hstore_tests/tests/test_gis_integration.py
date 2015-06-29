from django_hstore.apps import GEODJANGO_INSTALLED

if GEODJANGO_INSTALLED:
    from django.test import TestCase
    from django.contrib.gis.geos import GEOSGeometry
    from django_hstore_tests.models import Location

    class TestDictionaryFieldPlusGIS(TestCase):
        """ Test DictionaryField with gis backend """
        pnt1 = GEOSGeometry('POINT(65.5758316 57.1345383)')
        pnt2 = GEOSGeometry('POINT(65.2316 57.3423233)')

        def setUp(self):
            Location.objects.all().delete()

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

        def test_manager(self):
            from django_hstore.managers import HStoreGeoManager
            isinstance(Location.objects, HStoreGeoManager)
            hasattr(Location.objects, 'hpeek')
            hasattr(Location.objects, 'hslice')
            hasattr(Location.objects, 'hkeys')

    # noqa
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
