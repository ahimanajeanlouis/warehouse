# Warehouse Management System (Django)

A complete beginner-friendly warehouse workflow:

**Receiving -> Putaway -> Inventory -> Picking -> Packing -> Shipping**

## Main features

- User registration and login
- Protected warehouse pages
- Dashboard with operation counts and activity log
- FEFO-style expiry alerts
- Product/inventory management
- Receiving that automatically updates usable inventory
- Putaway tracking and storage locations
- Picking with SKU validation and stock checking
- Picking reduces available inventory so stock cannot go negative
- Packing can only use quantities that were actually picked
- Shipping can only ship quantities that were actually packed
- Responsive navigation for desktop and mobile
- Django messages and form validation
- SQLite for local development
- PostgreSQL-compatible `DATABASE_URL` for deployment

## Local setup

Create/activate a virtual environment, then:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Test workflow

1. Register a normal user.
2. Login.
3. Add a product, or receive goods using an SKU.
4. Receiving good-condition goods automatically increases inventory.
5. Put the received batch into a storage location.
6. Create a picking task using the exact product name and SKU.
7. The system checks available stock and subtracts the picked quantity.
8. Pack the same order/product.
9. Ship the packed quantity to a destination.
10. Check the dashboard activity log and inventory.

## Deployment

Set these environment variables on the hosting platform:

- `SECRET_KEY` = a long random secret
- `DEBUG` = `False`
- `DATABASE_URL` = your PostgreSQL connection string
- `TIME_ZONE` = `Africa/Kigali`

The Render build command runs migrations before starting Gunicorn:

```text
pip install -r requirements.txt && python manage.py migrate
```

For production, use PostgreSQL rather than SQLite because a normal Render web service has an ephemeral filesystem.

## Important business rule

Inventory is reduced at **Picking**, not again at Shipping. This prevents the same stock from being deducted twice.

Shipping is allowed only when enough quantity has already been packed for that order and product.
