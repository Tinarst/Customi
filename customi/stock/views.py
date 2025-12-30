from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from stock.models import Category, Product, Store, Feedback
from stock.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    StoreSerializer,
    FeedbackSerializer
)


class CategoryList(ListAPIView):
    queryset = Category.objects.select_related("parent").order_by("-pk")
    serializer_class = CategorySerializer

class CategoryDetail(RetrieveAPIView):
    queryset = Category.objects.select_related("parent")
    serializer_class = CategorySerializer


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            "name": ["icontains"]
        }
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering_fields = ["-rating", "-created_at"]

    def get_queryset(self):
        return Product.objects.with_best_price().with_rating().with_stock()

    def get_serializer_class(self, *args, **kwargs):
        if self.kwargs.get(self.lookup_url_kwarg, None):
            return ProductDetailSerializer
        return ProductSerializer


    @action(methods=["GET"], detail=True)
    def review_list(self, request, pk=None):
        product = self.get_object()
        queryset = Feedback.objects.filter(product_store__product=product)
    
        page = self.paginate_queryset(queryset)
        if page:
            serializer = FeedbackSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = FeedbackSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoreDetail(RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    
class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.select_related("user", "product_store")
