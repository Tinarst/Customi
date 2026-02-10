from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    GenericAPIView,
    ListAPIView,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from cart.models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer
from stock.models import ProductStore


@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated])
def cart_view(request: Request):
    user = request.user
    try:
        user_cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        data = {"items": []}
    else:
        serializer = CartSerializer(instance=user_cart)
        data = serializer.data
    finally:
        return Response(data, status=status.HTTP_200_OK)


# class CartView(ModelViewSet):
#     serializer_class = CartSerializer
#     queryset = Cart.objects.select_related("user")
#     permission_classes = [IsAuthenticated]
#     pagination_class = None

#     def list(self, request, *args, **kwargs):
#         user_cart = Cart.objects.get(user=request.user)
#         serializer = CartSerializer(instance=user_cart)
#         return Response(serializer.data, status=status.HTTP_200_OK)


def empty_cart(cart: Cart):
    CartItem.objects.filter(cart=cart).delete()


class CartItemAPIView(ModelViewSet):
    serializer_class = CartItemSerializer
    queryset = CartItem.objects.select_related("cart")
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def __get_cart(self, user):
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return None
        return cart

    def get_queryset(self):
        cart = self.__get_cart(self.request.user)

        return cart.cartitem_cart.all() if cart else cart

    @action(methods=["POST"], detail=True)
    def add_to_cart(self, request, pk=None):
        product_store = get_object_or_404(ProductStore, pk=pk)

        cart = self.__get_cart(request.user)
        if not cart:
            cart = Cart.objects.create(user=request.user)

        cart_item = CartItem.objects.create(cart=cart, product_store=product_store)
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
