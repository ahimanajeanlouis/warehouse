from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_page, name="logout"),
    path("receiving/", views.receiving_page, name="receiving"),
    path("putaway/", views.putaway_page, name="putaway"),
    path("inventory/", views.inventory_page, name="inventory"),
    path("picking/", views.picking_page, name="picking"),
    path("packing/", views.packing_page, name="packing"),
    path("shipping/", views.shipping_page, name="shipping"),
    path("suppliers/", views.suppliers_page, name="suppliers"),
    path("customers/", views.customers_page, name="customers"),
    path("locations/", views.locations_page, name="locations"),
    path("adjustments/", views.adjustments_page, name="adjustments"),
    path("adjustments/<int:adjustment_id>/<str:decision>/", views.review_adjustment, name="review_adjustment"),
    path("reports/", views.reports_page, name="reports"),
]
