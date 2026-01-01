from django.contrib import admin
from stock.models import Product, ProductImage, ProductStore, Store, Category, StoreFeedback, ProductFeedback

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductStore)
admin.site.register(Store)
admin.site.register(Category)
admin.site.register(StoreFeedback)
admin.site.register(ProductFeedback)