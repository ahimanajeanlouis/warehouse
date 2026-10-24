from django.db import models


# =========================
# PRODUCTS (INVENTORY)
# =========================
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=0)
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    unit_of_measure = models.CharField(max_length=30, default="piece")
    reorder_level = models.PositiveIntegerField(default=5)
    lead_time_days = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# WAREHOUSE ACTIVITIES
# =========================
class WarehouseActivity(models.Model):

    ACTIVITY_TYPES = [
        ('RECEIVING', 'Receiving'),
        ('PUTAWAY', 'Putaway'),
        ('INVENTORY', 'Inventory'),
        ('PICKING', 'Picking'),
        ('PACKING', 'Packing'),
        ('SHIPPING', 'Shipping'),
    ]

    STATUS_TYPES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELAYED', 'Delayed'),
    ]

    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    reference = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


# =========================
# RECEIVING MODULE
# =========================
class Receiving(models.Model):
    CONDITION_GOOD = 'GOOD'
    CONDITION_DAMAGED = 'DAMAGED'

    CONDITION_CHOICES = [
        (CONDITION_GOOD, 'Good'),
        (CONDITION_DAMAGED, 'Damaged'),
    ]

    product_name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,
        default=CONDITION_GOOD,
    )
    supplier = models.CharField(max_length=100)
    received_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='RECEIVED')
    inventory_updated = models.BooleanField(default=False)

    def total_price(self):
        return self.quantity * self.unit_price   

    
  
    def __str__(self):
        return self.product_name

class Putaway(models.Model):
    receiving = models.ForeignKey(
        Receiving,
        on_delete=models.CASCADE
    )

    location = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        default='STORED'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.receiving.product_name

class Picking(models.Model):
    product_name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50)
    quantity = models.IntegerField()
    order_reference = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_reference

class Packing(models.Model):
    order_ref = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default='PACKED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_ref

class Shipping(models.Model):
    order_ref = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    destination = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='IN_TRANSIT')
    shipped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_ref

# =========================
# MASTER DATA AND STOCK CONTROL (WMS UPDATE)
# =========================
class Supplier(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} — {self.name}"


class Customer(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} — {self.name}"


class WarehouseLocation(models.Model):
    warehouse = models.CharField(max_length=100, default="Main Warehouse")
    zone = models.CharField(max_length=50, blank=True)
    aisle = models.CharField(max_length=50, blank=True)
    rack = models.CharField(max_length=50, blank=True)
    bin = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["warehouse", "zone", "aisle", "rack", "bin"], name="unique_warehouse_bin")]
        ordering = ["warehouse", "zone", "aisle", "rack", "bin"]

    def __str__(self):
        parts = [self.warehouse, self.zone, self.aisle, self.rack, self.bin]
        return " / ".join(part for part in parts if part)


class ProductLocation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="locations")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.PROTECT, related_name="stock")
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["product", "location"], name="unique_product_location")]

    def __str__(self):
        return f"{self.product.sku} at {self.location}: {self.quantity}"


class StockAdjustment(models.Model):
    REASONS = [
        ("COUNT", "Cycle count correction"),
        ("DAMAGE", "Damaged goods"),
        ("EXPIRY", "Expired goods"),
        ("LOSS", "Missing / lost stock"),
        ("FOUND", "Found stock"),
        ("OTHER", "Other"),
    ]
    STATUSES = [("PENDING", "Pending approval"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")]
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    change_quantity = models.IntegerField(help_text="Use a positive number to add stock and a negative number to remove stock.")
    reason = models.CharField(max_length=10, choices=REASONS)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="PENDING")
    requested_by = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="stock_adjustments_requested")
    approved_by = models.ForeignKey("auth.User", on_delete=models.PROTECT, null=True, blank=True, related_name="stock_adjustments_approved")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Adjustment #{self.pk} — {self.product.sku} ({self.status})"


class AuditLog(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_reference = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — {self.object_type} — {self.created_at:%Y-%m-%d %H:%M}"


class StockTransfer(models.Model):
    STATUSES = [("PENDING", "Pending"), ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled")]
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    source = models.ForeignKey(WarehouseLocation, on_delete=models.PROTECT, related_name="transfers_out")
    destination = models.ForeignKey(WarehouseLocation, on_delete=models.PROTECT, related_name="transfers_in")
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=STATUSES, default="PENDING")
    requested_by = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transfer #{self.pk} — {self.product.sku}"
