# Warehouse Management System — Update Notes

This update extends the existing Django WMS while preserving its original receiving, putaway, inventory, picking, packing, and shipping pages.

## Added in this update
- Supplier records with code, contact, email, phone, and address.
- Customer records with code, contact, billing address, and shipping address.
- Product master fields: barcode, category, unit of measure, reorder level, and supplier lead time in days.
- Warehouse location hierarchy fields: warehouse, zone, aisle, rack, and bin.
- Product-to-location stock mapping model.
- Stock adjustment requests with reason codes, pending/approved/rejected states, and manager/staff approval. Inventory changes only after approval, and negative inventory is blocked.
- Audit log model and logging for supplier/customer/location creation and stock adjustment reviews.
- Reports page showing master-data counts, low stock based on each product's reorder level, pending adjustments, and recent audit events.
- Django admin registrations for the new records.

## Run the update
1. Back up your database first.
2. Replace the old project files with this updated project (or merge the changes if you have made local edits).
3. Activate your project's virtual environment.
4. Run:
   ```bash
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```
5. Log in and visit `/suppliers/`, `/customers/`, `/locations/`, `/adjustments/`, and `/reports/`.
6. A staff user can approve/reject stock adjustments. Create or promote a manager account using Django admin if needed.

## Important scope notes
- This is a foundational update, not yet a complete enterprise WMS.
- Existing receiving records still keep supplier names as text for backward compatibility; linking receiving directly to supplier master records is a follow-up migration.
- Product-location mapping and stock-transfer records are available as data models/admin records, but transfer execution and automatic bin-level stock allocation are not yet connected to the day-to-day receiving/picking flow.
- The current low-stock report uses each product's reorder level. Barcode scanning devices, carrier integrations, full staff role matrix, cycle counting, purchase orders, mobile scanner UI, and automated backups remain future work.
- Test on a copy of your database before deploying to production. This environment did not have Django installed and could not download dependencies, so runtime checks were not possible here; Python syntax compilation passed.
