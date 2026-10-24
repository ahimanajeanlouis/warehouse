from django.contrib import admin

from .models import (
    Customer,
    InventoryMovement,
    Location,
    Order,
    OrderItem,
    Packing,
    Picking,
    Product,
    Putaway,
    Receiving,
    Shipping,
    Supplier,
    UserProfile,
    WarehouseActivity,
)


admin.site.register(UserProfile)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Location)
admin.site.register(Product)
admin.site.register(WarehouseActivity)
admin.site.register(InventoryMovement)
admin.site.register(Receiving)
admin.site.register(Putaway)
admin.site.register(Picking)
admin.site.register(Packing)
admin.site.register(Shipping)
admin.site.register(Order)
admin.site.register(OrderItem)
