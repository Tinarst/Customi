from django.test import TestCase
from stock.models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.product_test_1 = Product.objects.create(name="test1")
        self.product_test_2 = Product.objects.create(name="test2")
    
    def test_product_stock(self):
        ...

    