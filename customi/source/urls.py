"""
URL configuration for source project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from stock.views import CategoryViewSet, ProductViewSet, StoreViewSet, MyStoreGenericAPIView, MyStoreItemsViewSet
from account.views import RequestOTP, VerifyOTP, AccountView, AddressViewSet
from cart.views import cart_view, CartItemAPIView
from order.views import OrderViewSet, MyOrdersViewSet

router = routers.DefaultRouter()
router.register("api/products", ProductViewSet, basename="product")
router.register("api/stores", StoreViewSet)
router.register("api/categories", CategoryViewSet)
router.register("api/myuser/address", AddressViewSet)
router.register("api/mycart/items", CartItemAPIView)
router.register("api/orders", OrderViewSet)
router.register("api/admin/categories", CategoryViewSet, basename="category-admin")
router.register("api/mystore/items", MyStoreItemsViewSet, basename="mystore-item")
router.register("api/mystore/orderitems", MyOrdersViewSet)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
    ] + [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
    + [ 
       path("api/accounts/token/refresh/", TokenRefreshView.as_view()),
    ] + [
        path("api/accounts/request-otp/", RequestOTP.as_view(), name="request-otp"),
        path("api/accounts/verify-otp/", VerifyOTP.as_view(), name="verify-otp"),
        path("api/myuser/", AccountView.as_view()),
    ] + [
        path("api/mycart/", cart_view),
    ] +
    [
        path("api/myuser/register_as_seller/", MyStoreGenericAPIView.as_view()),
        path("api/mystore/", MyStoreGenericAPIView.as_view())
    ]
)

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
