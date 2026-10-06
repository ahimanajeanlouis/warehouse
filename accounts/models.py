from django.db import models


# =========================
# PRODUCTS (INVENTORY)
# =========================
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.IntegerField(default=0)
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

