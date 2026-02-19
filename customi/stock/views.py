from django.db.models import Q
from rest_framework.generics import (
    GenericAPIView,
)
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.permissions import (
    IsAuthenticated,
    SAFE_METHODS,
)
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import FilterSet
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from stock.models import (
    Category,
    Product,
    Store,
    ProductFeedback,
    StoreFeedback,
    ProductStore,
)
from stock.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductStoreSerializer,
    ProductSerializerWrite,
    StoreSerializer,
    ProductFeedbackSerializer,
    StoreFeedbackSerializer,
)
from core.permissions import ReadOnlyOrSeller, HasStoreOrSeller
from .mixins import CreateWithCreatorMixin
from account.models import CustomUser
from order.models import OrderItem, Order
import logging

logger = logging.getLogger("customi")


class CategoryViewSet(CreateWithCreatorMixin, ModelViewSet):
    queryset = Category.objects.select_related("parent").order_by("-pk")
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrSeller]

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.filter(category=self.get_object()).exclude(
            created_by=request.user
        )
        product_store = ProductStore.objects.filter(
            product__category=self.get_object()
        ).exclude(store__seller=request.user)
        if product.exists() or product_store.exists():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return super().destroy(request, *args, **kwargs)


def can_add_review(user: CustomUser, product: Product = None, store: Store = None):
    if store is not None:
        if OrderItem.objects.filter(
            order__user=user,
            product_store__store=store,
            order__status__in=[Order.OrderStatus.PAID, Order.OrderStatus.SHIPPED],
        ).exists():
            return True
    elif product is not None:
        if OrderItem.objects.filter(
            order__user=user,
            product_store__product=product,
            order__status__in=[Order.OrderStatus.PAID, Order.OrderStatus.SHIPPED],
        ).exists():
            return True
    return False


class ProductFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        price_max = self.data.get("price_max", None)
        price_min = self.data.get("price_min", None)
        category = self.data.get("category", None)
        if category:
            queryset = queryset.products_with_parent(category)

        if price_max:
            queryset = queryset.filter(productstore_product__price__lt=float(price_max))

        if price_min:
            queryset = queryset.filter(productstore_product__price__gt=float(price_min))

        return queryset


class ProductViewSet(CreateWithCreatorMixin, ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [ReadOnlyOrSeller]
    lookup_url_kwarg = "pk"
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = ["created_at", "-rating"]

    def get_queryset(self):
        return Product.objects.with_best_price().with_rating()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            return ProductSerializer
        return ProductSerializerWrite

    @action(methods=["GET"], detail=True)
    def review_list(self, request, pk=None):
        product = self.get_object()
        queryset = ProductFeedback.objects.filter(product=product)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = ProductFeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductFeedbackSerializer(queryset, many=True)
        if not serializer.data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def review_create(self, request, pk=None):
        product = self.get_object()

        serializer = ProductFeedbackSerializer(
            data=self.request.data,
            context={"product": product, "user": self.request.user},
        )

        if not can_add_review(user=self.request.user, product=product):
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        product_store = ProductStore.objects.filter(product=self.get_object()).exclude(
            store__seller=request.user
        )
        if product_store.exists():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return super().destroy(request, *args, **kwargs)


class StoreViewSet(ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    @action(methods=["GET"], detail=True)
    def review_list(self, request, pk=None):
        store = self.get_object()
        queryset = StoreFeedback.objects.filter(store=store)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = StoreFeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StoreFeedbackSerializer(queryset, many=True)
        if not serializer.data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
    @action(methods=["POST"], detail=True)
    def review_create(self, request, pk=None):
        store = self.get_object()

        serializer = StoreFeedbackSerializer(
            data=self.request.data, context={"store": store, "user": self.request.user}
        )

        if not can_add_review(user=self.request.user, store=store):
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyStoreGenericAPIView(
    CreateWithCreatorMixin, RetrieveModelMixin, UpdateModelMixin, GenericAPIView
):
    queryset = Store.objects.select_related("seller")
    serializer_class = StoreSerializer
    permission_classes = [HasStoreOrSeller]
    pagination_class = None

    def get_object(self):
        return self.request.user.store_user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def post(self, requset, *args, **kwargs):
        return self.create(requset, *args, **kwargs)


class MyStoreItemsViewSet(CreateWithCreatorMixin, ModelViewSet):
    queryset = ProductStore.objects.select_related("product", "store")
    serializer_class = ProductStoreSerializer
    permission_classes = [ReadOnlyOrSeller]

    def get_queryset(self):
        return ProductStore.objects.filter(store__seller=self.request.user)
