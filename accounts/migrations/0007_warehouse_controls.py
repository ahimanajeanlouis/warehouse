# Warehouse master data, stock control, and audit trail.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_receiving_inventory_updated'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(model_name='product', name='barcode', field=models.CharField(blank=True, db_index=True, max_length=100)),
        migrations.AddField(model_name='product', name='category', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='product', name='unit_of_measure', field=models.CharField(default='piece', max_length=30)),
        migrations.AddField(model_name='product', name='reorder_level', field=models.PositiveIntegerField(default=5)),
        migrations.AddField(model_name='product', name='lead_time_days', field=models.PositiveIntegerField(default=0)),
        migrations.CreateModel(name='Customer', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('code', models.CharField(max_length=30, unique=True)), ('name', models.CharField(max_length=150)),
            ('contact_person', models.CharField(blank=True, max_length=100)), ('email', models.EmailField(blank=True, max_length=254)),
            ('phone', models.CharField(blank=True, max_length=30)), ('billing_address', models.TextField(blank=True)),
            ('shipping_address', models.TextField(blank=True)), ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='Supplier', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('code', models.CharField(max_length=30, unique=True)), ('name', models.CharField(max_length=150)),
            ('contact_person', models.CharField(blank=True, max_length=100)), ('email', models.EmailField(blank=True, max_length=254)),
            ('phone', models.CharField(blank=True, max_length=30)), ('address', models.TextField(blank=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='WarehouseLocation', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('warehouse', models.CharField(default='Main Warehouse', max_length=100)), ('zone', models.CharField(blank=True, max_length=50)),
            ('aisle', models.CharField(blank=True, max_length=50)), ('rack', models.CharField(blank=True, max_length=50)),
            ('bin', models.CharField(max_length=50)), ('is_active', models.BooleanField(default=True)),
        ], options={'ordering': ['warehouse', 'zone', 'aisle', 'rack', 'bin']}),
        migrations.CreateModel(name='AuditLog', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('action', models.CharField(max_length=100)), ('object_type', models.CharField(max_length=100)),
            ('object_reference', models.CharField(blank=True, max_length=100)), ('details', models.TextField(blank=True)),
            ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['-created_at']}),
        migrations.CreateModel(name='ProductLocation', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('quantity', models.PositiveIntegerField(default=0)), ('updated_at', models.DateTimeField(auto_now=True)),
            ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock', to='accounts.warehouselocation')),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='accounts.product')),
        ]),
        migrations.CreateModel(name='StockAdjustment', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('change_quantity', models.IntegerField(help_text='Use a positive number to add stock and a negative number to remove stock.')),
            ('reason', models.CharField(choices=[('COUNT', 'Cycle count correction'), ('DAMAGE', 'Damaged goods'), ('EXPIRY', 'Expired goods'), ('LOSS', 'Missing / lost stock'), ('FOUND', 'Found stock'), ('OTHER', 'Other')], max_length=10)),
            ('notes', models.TextField(blank=True)), ('status', models.CharField(choices=[('PENDING', 'Pending approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10)),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('reviewed_at', models.DateTimeField(blank=True, null=True)),
            ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='stock_adjustments_approved', to=settings.AUTH_USER_MODEL)),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.product')),
            ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_adjustments_requested', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='StockTransfer', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('quantity', models.PositiveIntegerField()), ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=12)),
            ('created_at', models.DateTimeField(auto_now_add=True)), ('completed_at', models.DateTimeField(blank=True, null=True)),
            ('destination', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_in', to='accounts.warehouselocation')),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.product')),
            ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ('source', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_out', to='accounts.warehouselocation')),
        ]),
        migrations.AddConstraint(model_name='warehouselocation', constraint=models.UniqueConstraint(fields=('warehouse', 'zone', 'aisle', 'rack', 'bin'), name='unique_warehouse_bin')),
        migrations.AddConstraint(model_name='productlocation', constraint=models.UniqueConstraint(fields=('product', 'location'), name='unique_product_location')),
    ]
