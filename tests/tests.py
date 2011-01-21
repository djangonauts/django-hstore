
import unittest
from .app.models import Bag, Ref

class TestCase(unittest.TestCase):
    def setUp(self):
        Bag.objects.all().delete()
        Ref.objects.all().delete()

class TestDictionaryField(TestCase):
    def test_null_instantiation(self):
        bag = Bag.objects.create(name='bag')
        self.assertTrue(isinstance(bag.data, dict))
        self.assertEquals(bag.data, {})

    
