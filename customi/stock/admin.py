from django.contrib import admin
from stock.models import Product, ProductStore, Store, Category, Feedback

admin.site.register(Product)
admin.site.register(ProductStore)
admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Feedback)