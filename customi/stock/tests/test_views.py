from rest_framework.test import APITestCase
from django.urls import reverse
from stock.models import Product, ProductStore, Store, Category
from account.models import CustomUser


class ProductStoreViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone="09123456789", userType=True)
        self.store = Store.objects.create(
            seller=self.user, name="store", description="test"
        )
        self.client.force_authenticate(user=self.user)

    def test_cant_add_productstore_from_unavailable_product(self):
        product = Product.objects.create(name="test", is_active=False)
        path = reverse("mystore-item-list")
        data = {
            "id": product.pk,
            "stock": 1,
            "discount_price": 0,
            "price": 10000,
        }
        response = self.client.post(data=data, path=path)

        self.assertEqual(response.status_code, 400)


class CategoryViewTest(APITestCase):

    def setUp(self):
        self.owner = CustomUser.objects.create("09123456789")
        self.user = CustomUser.objects.create("09912345678")
        Store.objects.create(name="test_store", seller=self.owner)
        self.category = Category.objects.create(
            name="test_category", created_by=self.owner
        )
        self.client.force_authenticate(user=self.owner)
        self.path = reverse("category-admin-detail", args=[self.category.pk])
        return super().setUp()

    def test_cant_delete_category_with_product(self):
        """If a user other than the <category creator>:<category.created_by> creates a product from the category,
        the category will not be allowed to be deleted"""

        Product.objects.create(
            name="test_product", category=self.category, created_by=self.user
        )
        response = self.client.delete(path=self.path)

        self.assertEqual(response.status_code, 406)

    def test_cant_delete_category_with_product_store(self):
        """If a user other than the <category creator>:<category.created_by> creates a Product-Store
        from a product that has an existing category,
        the category will not be allowed to be deleted."""

        user_store = Store.objects.create(name="test2_store", seller=self.user)
        product = Product.objects.create(
            name="test_product", category=self.category, created_by=self.owner
        )
        ProductStore.objects.create(product=product, store=user_store, price=10000)
        response = self.client.delete(path=self.path)

        self.assertEqual(response.status_code, 406)


class ProductViewTest(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create("09123456789")
        self.user = CustomUser.objects.create("09912345678")
        self.owner_store = Store.objects.create(name="test_store", seller=self.owner)
        self.category = Category.objects.create(
            name="test_category", created_by=self.owner
        )
        self.product = Product.objects.create(
            name="test_product", category=self.category, created_by=self.owner
        )
        ProductStore.objects.create(product=self.product, store=self.owner_store, price=20000)
        self.client.force_authenticate(user=self.owner)
        self.path = reverse("product-detail", args=[self.product.pk])

    def test_cant_delete_product_with_product_store(self):
        user_store = Store.objects.create(name="test2_store", seller=self.user)
        ProductStore.objects.create(product=self.product, store=user_store, price=10000)
        response = self.client.delete(path=self.path)

        self.assertEqual(response.status_code, 406)

    def test_can_delete_product_without_product_store(self): 
        response = self.client.delete(path=self.path)

        self.assertEqual(response.status_code, 204)
        
    def test_can_delete_product_with_owner_product_store(self):
        ProductStore.objects.create(product=self.product, store=self.owner_store, price=20000)
        response = self.client.delete(path=self.path)

        self.assertEqual(response.status_code, 204)
