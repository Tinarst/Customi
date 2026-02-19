from rest_framework import serializers
from stock.models import (
    Category,
    Product,
    ProductStore,
    ProductImage,
    Store,
    ProductFeedback,
    StoreFeedback,
)
from account.serializers import AccountSerializer
from account.models import CustomUser
from source.settings import BASE_DIR


class CategorySerializer(serializers.ModelSerializer):
    """seprate for read-only serializer and parents"""

    parents = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "image",
            "is_active",
            "parents",
            "parent",
        ]

    def get_parents(self, obj: Category):
        parents = []
        current = obj.parent
        while current:
            parents.append({"id": current.id, "name": current.name})
            current = current.parent
        return list(reversed(parents))

    def to_internal_value(self, data):
        data = data.copy()
        if data.get("parent", None) == "null":
            data["parent"] = None
        return super().to_internal_value(data)

    def create(self, validated_data):
        validated_data["created_by"] = self.context.get("user", None)
        return super().create(validated_data)


class StoreSerializer(serializers.ModelSerializer):

    seller = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Store
        fields = ["id", "name", "seller", "description"]

    def create(self, validated_data):
        seller = self.context.get("user", None)
        validated_data["seller"] = seller
        store = super().create(validated_data)
        seller.role = CustomUser.UserRole.SELLER
        seller.save()
        return store


class ProductStoreSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )

    class Meta:
        model = ProductStore
        fields = [
            "id",
            "price",
            "stock",
            "store",
            "discount_price",
            "product",
            "is_active",
        ]

    def validate_price(self, price):
        price = float(price)
        if 1000 <= price <= 200000000:
            return price
        print("The acceptable price is between 1000 and 200,000,000")
        raise serializers.ValidationError(
            "The acceptable price is between 1000 and 200,000,000"
        )

    def validate_discount_price(self, discount_price):
        discount_price = float(discount_price)
        if discount_price == 0.0:
            return None
        if 1000 <= discount_price <= 200000000 or discount_price == 0.0:
            return discount_price
        print("The acceptable discount_price is between 1000 and 200,000,000")
        raise serializers.ValidationError(
            "The acceptable discount_price is between 1000 and 200,000,000"
        )

    def validate(self, attrs):
        discount_price = attrs.get("discount_price", None)
        if not attrs["product"].is_active:
            print("cant add unavailable product") 
            raise serializers.ValidationError("cant add unavailable product")
        if not discount_price or discount_price < attrs["price"]:
            return super().validate(attrs)
        print("discount price should be lower than price")
        raise serializers.ValidationError(
            "discount price should be lower than price"
        )
        

    def create(self, validated_data):
        validated_data["store"] = self.context.get("user").store_user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["product"] = {"name": instance.product.name}
        return representation


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    """Root Products"""

    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(
        source="productimage_product", many=True, read_only=True
    )
    rating = serializers.IntegerField(read_only=True)
    best_seller = ProductStoreSerializer(read_only=True)
    sellers = ProductStoreSerializer(source="productstore_product", many=True)
    best_price = serializers.FloatField(read_only=True)
    stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "best_price",
            "best_seller",
            "sellers",
            "category",
            "description",
            "id",
            "name",
            "rating",
            "stock",
            "images",
            "created_at",
        ]
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProductSerializerWrite(serializers.ModelSerializer):
    """use just for POST, PUT"""

    images = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_null=True
    )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "images",
            "is_active"
        ]

    def create(self, validated_data):
        images = validated_data.pop("images", None)
        validated_data["created_by"] = self.context.get("user", None)
        product = super().create(validated_data)
        for img in images:
            ProductImage.objects.create(image=img, product=product)
        return product

    def update(self, instance, validated_data: dict):
        images = validated_data.pop("images", None)
        if images:
            for img in images:
                ProductImage.objects.create(image=img, product=instance)
        return super().update(instance, validated_data)


class ProductFeedbackSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ProductFeedback
        fields = ["id", "user", "rating", "comment", "created_at"]

    def validate(self, validated_data: dict):
        user = self.context["user"]
        product = self.context["product"]
        if self.Meta.model.objects.filter(product=product, user=user).exists():
            print(f"User {user} has been commented recently")
            raise serializers.ValidationError(
                f"User {user} has been commented recently"
            )

        return validated_data

    def create(self, validated_data: dict):
        product_feedback = self.Meta.model(
            user=self.context["user"], product=self.context["product"], **validated_data
        )
        product_feedback.save()

        return product_feedback


class StoreFeedbackSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)

    class Meta:
        model = StoreFeedback
        fields = ["id", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "user"]

    def validate(self, validated_data: dict):
        user = self.context["user"]
        store = self.context["store"]
        if self.Meta.model.objects.filter(store=store, user=user).exists():
            print(f"User {user} has been commented recently")
            raise serializers.ValidationError(
                f"User {user} has been commented recently"
            )

        return validated_data

    def create(self, validated_data: dict):
        store_feedback = self.Meta.model(
            user=self.context["user"], store=self.context["store"], **validated_data
        )
        store_feedback.save()
        return store_feedback
