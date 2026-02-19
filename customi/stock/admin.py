from django.contrib import admin
from stock.models import Product, ProductImage, ProductStore, Store, Category, StoreFeedback, ProductFeedback

class ProductAdmin(admin.ModelAdmin):
    search_fields = ["name", "category__name"]
    list_filter = ["name", "created_by"]
    list_display = ["id", "name", "created_by", "category"]

class StoreAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class ProductStoreAdmin(admin.ModelAdmin):
    ...
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["parent", "created_by"]
    list_display = ["id", "name", "parent"]
    
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductStore)
admin.site.register(Store)
admin.site.register(Category, CategoryAdmin)
admin.site.register(StoreFeedback)
admin.site.register(ProductFeedback)