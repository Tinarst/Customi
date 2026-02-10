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

from stock.views import CategoryViewSet, ProductViewSet, StoreViewSet
from account.views import RequestOTP, VerifyOTP, AccountView, AddressViewSet
from cart.views import cart_view, CartItemAPIView
from order.views import OrderViewSet

router = routers.DefaultRouter()
router.register("api/products", ProductViewSet)
router.register("api/stores", StoreViewSet)
router.register("api/categories", CategoryViewSet)
router.register("api/myuser/address", AddressViewSet)
router.register("api/mycart/items", CartItemAPIView)
router.register("api/orders", OrderViewSet)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
    ]
    + [ 
       path("api/accounts/token/refresh/", TokenRefreshView.as_view()),
    ] + [
        path("api/accounts/request-otp/", RequestOTP.as_view()),
        path("api/accounts/verify-otp/", VerifyOTP.as_view()),
        path("api/myuser/", AccountView.as_view()),
    ] + [
        path("api/mycart/", cart_view),
    ]
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + router.urls
