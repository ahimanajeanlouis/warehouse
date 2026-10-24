from django.contrib.auth.models import User
from django.db import models


# =========================
# PRODUCTS (INVENTORY)
# =========================
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=0)
    barcode = models.CharField(max_length=50, blank=True, default="")
    category = models.CharField(max_length=50, blank=True, default="")
    reorder_level = models.IntegerField(default=0)
    unit_of_measure = models.CharField(max_length=20, default="pcs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("staff", "Staff"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")
    phone = models.CharField(max_length=30, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    address = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    address = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    warehouse = models.CharField(max_length=100, default="Main Warehouse")
    zone = models.CharField(max_length=50, blank=True, default="")
    aisle = models.CharField(max_length=50, blank=True, default="")
    rack = models.CharField(max_length=50, blank=True, default="")
    bin = models.CharField(max_length=50, blank=True, default="")
    capacity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


# =========================
# WAREHOUSE ACTIVITIES
# =========================
class WarehouseActivity(models.Model):
    ACTIVITY_TYPES = [
        ("RECEIVING", "Receiving"),
        ("PUTAWAY", "Putaway"),
        ("INVENTORY", "Inventory"),
        ("PICKING", "Picking"),
        ("PACKING", "Packing"),
        ("SHIPPING", "Shipping"),
    ]

    STATUS_TYPES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("DELAYED", "Delayed"),
    ]

    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    reference = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


class InventoryMovement(models.Model):
    MOVEMENT_CHOICES = [
        ("RECEIVING", "Receiving"),
        ("PUTAWAY", "Putaway"),
        ("PICKING", "Picking"),
        ("PACKING", "Packing"),
        ("SHIPPING", "Shipping"),
        ("ADJUSTMENT", "Adjustment"),
        ("TRANSFER", "Transfer"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True, default="")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type}"


# =========================
# RECEIVING MODULE
# =========================
class Receiving(models.Model):
    CONDITION_GOOD = "GOOD"
    CONDITION_DAMAGED = "DAMAGED"

    CONDITION_CHOICES = [
        (CONDITION_GOOD, "Good"),
        (CONDITION_DAMAGED, "Damaged"),
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
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    batch_number = models.CharField(max_length=50, blank=True, default="")
    recipient = models.CharField(max_length=100, blank=True, default="")
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default="RECEIVED")
    inventory_updated = models.BooleanField(default=False)
    received_date = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.product_name


class Putaway(models.Model):
    receiving = models.ForeignKey(Receiving, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default="STORED")
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
    status = models.CharField(max_length=20, default="PACKED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_ref


class Shipping(models.Model):
    order_ref = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="IN_TRANSIT")
    shipped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_ref


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PICKING", "Picking"),
        ("PACKING", "Packing"),
        ("READY_TO_SHIP", "Ready to Ship"),
        ("SHIPPED", "Shipped"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    delivery_address = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PICKED", "Picked"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
    ]

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.CharField(max_length=50)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"
