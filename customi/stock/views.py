from django.db.models import Q
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    get_object_or_404,
    ListCreateAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
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
    ProductDetailSerializer,
    StoreSerializer,
    ProductFeedbackSerializer,
    StoreFeedbackSerializer,
)
from account.models import CustomUser
from order.models import OrderItem, Order


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.select_related("parent").order_by("-pk")
    serializer_class = CategorySerializer


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


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_url_kwarg = "pk"
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = ["created_at", "rating"]

    def get_queryset(self):
        return Product.objects.with_best_price().with_rating().with_stock()

    def get_serializer_class(self, *args, **kwargs):
        if self.kwargs.get(self.lookup_url_kwarg, None):
            return ProductDetailSerializer
        return ProductSerializer

    @action(methods=["GET"], detail=True)
    def review_list(self, request, pk=None):
        product = self.get_object()
        queryset = ProductFeedback.objects.filter(product=product)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = ProductFeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductFeedbackSerializer(queryset, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True)
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


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(methods=["GET"], detail=True)
    def review_list(self, request, pk=None):
        store = self.get_object()
        queryset = StoreFeedback.objects.filter(store=store)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = StoreFeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StoreFeedbackSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class StoreFeedbackView(ListCreateAPIView):
    queryset = StoreFeedback.objects.select_related("user", "store")
    serializer_class = StoreFeedbackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
