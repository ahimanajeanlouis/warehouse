from django.contrib import admin
from .models import (Product, WarehouseActivity, Receiving, Putaway, Picking, Packing, Shipping, Supplier, Customer, WarehouseLocation, ProductLocation, StockAdjustment, AuditLog, StockTransfer)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "barcode", "quantity", "unit_of_measure", "reorder_level")
    search_fields = ("name", "sku", "barcode", "category")
    list_filter = ("category", "unit_of_measure")

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "change_quantity", "reason", "status", "requested_by", "approved_by", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("product__name", "product__sku", "notes")
    readonly_fields = ("requested_by", "created_at", "reviewed_at")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "object_type", "object_reference")
    list_filter = ("action", "object_type", "created_at")
    search_fields = ("object_reference", "details", "user__username")
    readonly_fields = ("user", "action", "object_type", "object_reference", "details", "created_at")

admin.site.register([WarehouseActivity, Receiving, Putaway, Picking, Packing, Shipping, Supplier, Customer, WarehouseLocation, ProductLocation, StockTransfer])
