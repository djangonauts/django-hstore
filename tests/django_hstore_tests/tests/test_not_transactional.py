from django import VERSION as DJANGO_VERSION
from django.db import transaction, connection
from django.test import SimpleTestCase

from django_hstore.fields import HStoreDict

from django_hstore_tests.models import DataBag


class TestNotTransactional(SimpleTestCase):
    allow_database_queries = True

    if DJANGO_VERSION[:2] >= (1, 8):
        def setUp(self):
            # avoid error "connection already closed"
            connection.connect()

    def test_hstore_registring_in_transaction_block(self):
        obj1 = DataBag.objects.create(name='alpha1', data={'v': '1', 'v2': '3'})
        obj2 = DataBag.objects.create(name='alpha2', data={'v': '1', 'v2': '3'})
        # Close any existing connection before doing anything
        connection.close()
        with transaction.atomic():
            qs = DataBag.objects.filter(name__in=["alpha2", "alpha1"])
            self.assertIsInstance(qs[0].data, HStoreDict)
        obj1.delete()
        obj2.delete()
        connection.close()
