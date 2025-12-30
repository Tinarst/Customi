from rest_framework import serializers
from stock.models import Category, Product, ProductStore, ProductImage, Store, Feedback
from account.serializers import AccountSerializer


class CategorySerializer(serializers.ModelSerializer):
    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "is_active", "parents"]

    def get_parents(self, obj: Category):
        parents = []
        current = obj.parent
        while current:
            parents.append({"id": current.id, "name": current.name})
            current = current.parent
        return list(reversed(parents))



class CategoryDetailSerializer(CategorySerializer):
    """extending CategorySerializer with 'detail_url'"""

    detail_url = serializers.HyperlinkedIdentityField(
        view_name="category_detail",
        lookup_field="pk",
        read_only=True,
    )

    class Meta:
        model = Category
        fields = CategorySerializer.Meta.fields + ["detail_url"]



class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = ["id", "name", "seller", "description"]



class ProductStoreSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = ProductStore
        fields = ["id", "price", "stock", "store", "discount_price"]



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]



class ProductSerializer(serializers.ModelSerializer):
    """Root Products"""

    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(source="productimage_product", many=True)
    rating = serializers.CharField(read_only=True)
    best_seller = ProductStoreSerializer(read_only=True)
    best_price = serializers.FloatField(read_only=True)
    stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "best_price",
            "best_seller",
            "category",
            "description",
            "id",
            "name",
            "rating",
            "stock",
            "images",
        ]



class ProductDetailSerializer(ProductSerializer):
    """extending product serializer with all specific product sellers and detail_url category"""

    sellers = ProductStoreSerializer(source="productstore_product", many=True)

    class Meta:
        model = Product
        fields = ProductSerializer.Meta.fields + ["sellers", "created_at"]



        

class FeedbackSerializer(serializers.ModelSerializer):
    user = AccountSerializer()
    class Meta:
        model = Feedback
        fields = [
            "id",
            "user",
            "rating",
            "comment",
            "created_at"
        ]
