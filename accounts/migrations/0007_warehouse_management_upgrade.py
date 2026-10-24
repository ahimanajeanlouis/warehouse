from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_default_user_profile(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("accounts", "UserProfile")
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user, defaults={"role": "staff"})


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_receiving_inventory_updated"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="barcode",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="product",
            name="reorder_level",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="product",
            name="unit_of_measure",
            field=models.CharField(default="pcs", max_length=20),
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("staff", "Staff"), ("manager", "Manager"), ("admin", "Admin")], default="staff", max_length=20)),
                ("phone", models.CharField(blank=True, default="", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("contact_person", models.CharField(blank=True, default="", max_length=100)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("phone", models.CharField(blank=True, default="", max_length=30)),
                ("address", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("contact_person", models.CharField(blank=True, default="", max_length=100)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("phone", models.CharField(blank=True, default="", max_length=30)),
                ("address", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("warehouse", models.CharField(default="Main Warehouse", max_length=100)),
                ("zone", models.CharField(blank=True, default="", max_length=50)),
                ("aisle", models.CharField(blank=True, default="", max_length=50)),
                ("rack", models.CharField(blank=True, default="", max_length=50)),
                ("bin", models.CharField(blank=True, default="", max_length=50)),
                ("capacity", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="InventoryMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("movement_type", models.CharField(choices=[("RECEIVING", "Receiving"), ("PUTAWAY", "Putaway"), ("PICKING", "Picking"), ("PACKING", "Packing"), ("SHIPPING", "Shipping"), ("ADJUSTMENT", "Adjustment"), ("TRANSFER", "Transfer")], max_length=20)),
                ("quantity", models.IntegerField()),
                ("reference", models.CharField(blank=True, default="", max_length=100)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("location", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="accounts.location")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movements", to="accounts.product")),
            ],
        ),
        migrations.AddField(
            model_name="receiving",
            name="batch_number",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="receiving",
            name="recipient",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="receiving",
            name="supplier",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="accounts.supplier"),
        ),
        migrations.AddField(
            model_name="putaway",
            name="location",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="accounts.location"),
        ),
        migrations.AddField(
            model_name="shipping",
            name="customer",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="accounts.customer"),
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.CharField(max_length=50, unique=True)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("PICKING", "Picking"), ("PACKING", "Packing"), ("READY_TO_SHIP", "Ready to Ship"), ("SHIPPED", "Shipped"), ("CANCELLED", "Cancelled")], default="PENDING", max_length=20)),
                ("delivery_address", models.TextField(blank=True, default="")),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="accounts.customer")),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sku", models.CharField(max_length=50)),
                ("quantity", models.IntegerField()),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("PICKED", "Picked"), ("PACKED", "Packed"), ("SHIPPED", "Shipped")], default="PENDING", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="accounts.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="accounts.product")),
            ],
        ),
        migrations.RunPython(create_default_user_profile, migrations.RunPython.noop),
    ]
