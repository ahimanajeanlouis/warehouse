from django.contrib import admin
from .models import Product, WarehouseActivity, Receiving, Putaway, Picking, Packing, Shipping

admin.site.register(Product)
admin.site.register(WarehouseActivity)
admin.site.register(Receiving)
admin.site.register(Putaway)
admin.site.register(Picking)
admin.site.register(Packing)
admin.site.register(Shipping)
