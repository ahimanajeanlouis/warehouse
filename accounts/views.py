from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    PackingForm,
    PickingForm,
    ProductForm,
    PutawayForm,
    ReceivingForm,
    ShippingForm,
)
from .models import (
    Packing,
    Picking,
    Product,
    Putaway,
    Receiving,
    Shipping,
    WarehouseActivity,
)


# =========================
# AUTHENTICATION
# =========================

def register_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email is already registered.")
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")

    return render(request, "accounts/register.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/index.html")


def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# =========================
# DASHBOARD
# =========================

@login_required(login_url="login")
def dashboard(request):
    today = date.today()
    warning_date = today + timedelta(days=30)

    expiring_items = Receiving.objects.filter(
        expiry_date__isnull=False,
        quantity__gt=0,
    ).order_by("expiry_date")

    for item in expiring_items:
        if item.expiry_date <= today:
            item.row_class = "expired"
        elif item.expiry_date <= warning_date:
            item.row_class = "warning"
        else:
            item.row_class = "safe"

    context = {
        "products_count": Product.objects.count(),
        "receiving": Receiving.objects.count(),
        "putaway": Putaway.objects.count(),
        "inventory": Product.objects.count(),
        "picking": Picking.objects.count(),
        "packing": Packing.objects.count(),
        "shipping": Shipping.objects.count(),
        "activities": WarehouseActivity.objects.all().order_by("-created_at")[:15],
        "expiring_batches": expiring_items[:20],
        "today": today,
        "warning_date": warning_date,
    }
    return render(request, "accounts/dashboard.html", context)


# =========================
# PRODUCT / INVENTORY
# =========================

@login_required(login_url="login")
def add_product(request):
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product added successfully.")
        return redirect("inventory")

    return render(request, "accounts/add_product.html", {"form": form})


@login_required(login_url="login")
def inventory_page(request):
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product added successfully.")
        return redirect("inventory")

    products = Product.objects.all().order_by("name")
    low_stock = Product.objects.filter(quantity__lte=5).order_by("quantity", "name")

    return render(
        request,
        "accounts/inventory.html",
        {"form": form, "products": products, "low_stock": low_stock},
    )


# =========================
# RECEIVING
# =========================

@login_required(login_url="login")
def receiving_page(request):
    form = ReceivingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            data = form.save()

            # Good received stock becomes available inventory immediately.
            # Damaged goods remain in the receiving history but are not added
            # to usable stock.
            if data.condition == Receiving.CONDITION_GOOD:
                product, _ = Product.objects.get_or_create(
                    sku=data.sku,
                    defaults={"name": data.product_name, "quantity": 0},
                )
                product.name = data.product_name
                product.quantity += data.quantity
                product.save(update_fields=["name", "quantity"])

            WarehouseActivity.objects.create(
                activity_type="RECEIVING",
                reference=f"RCV-{data.sku}",
                status="COMPLETED",
            )

        messages.success(request, "Goods received and inventory updated.")
        return redirect("receiving")

    records = Receiving.objects.all().order_by("-received_date")
    return render(
        request,
        "accounts/receiving.html",
        {"form": form, "records": records},
    )


# =========================
# PUTAWAY
# =========================

@login_required(login_url="login")
def putaway_page(request):
    form = PutawayForm(request.POST or None)
    form.fields["receiving"].queryset = Receiving.objects.filter(status="RECEIVED")

    if request.method == "POST" and form.is_valid():
        putaway = form.save(commit=False)
        putaway.status = "STORED"
        putaway.save()

        putaway.receiving.status = "STORED"
        putaway.receiving.save(update_fields=["status"])

        WarehouseActivity.objects.create(
            activity_type="PUTAWAY",
            reference=f"PUT-{putaway.receiving.sku}",
            status="COMPLETED",
        )
        messages.success(request, "Product stored successfully.")
        return redirect("putaway")

    records = Putaway.objects.select_related("receiving").all().order_by("-created_at")
    return render(request, "accounts/putaway.html", {"form": form, "records": records})


# =========================
# PICKING
# =========================

@login_required(login_url="login")
def picking_page(request):
    form = PickingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        sku = form.cleaned_data["sku"].strip()
        quantity = form.cleaned_data["quantity"]

        with transaction.atomic():
            try:
                product = Product.objects.select_for_update().get(sku__iexact=sku)
            except Product.DoesNotExist:
                form.add_error("sku", "No inventory product exists with this SKU.")
            else:
                if product.quantity < quantity:
                    form.add_error(
                        "quantity",
                        f"Insufficient stock. Available quantity: {product.quantity}.",
                    )
                elif product.name.strip().lower() != form.cleaned_data["product_name"].strip().lower():
                    form.add_error(
                        "product_name",
                        f"SKU {product.sku} belongs to '{product.name}'.",
                    )
                else:
                    data = form.save()
                    product.quantity -= quantity
                    product.save(update_fields=["quantity"])

                    WarehouseActivity.objects.create(
                        activity_type="PICKING",
                        reference=f"PICK-{data.order_reference}",
                        status="COMPLETED",
                    )
                    messages.success(
                        request,
                        f"Picking completed. {quantity} unit(s) reserved for order {data.order_reference}.",
                    )
                    return redirect("picking")

    records = Picking.objects.all().order_by("-created_at")
    return render(request, "accounts/picking.html", {"form": form, "records": records})


# =========================
# PACKING
# =========================

@login_required(login_url="login")
def packing_page(request):
    form = PackingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order_ref = form.cleaned_data["order_ref"].strip()
        product = form.cleaned_data["product"]
        quantity = form.cleaned_data["quantity"]

        picked_qty = sum(
            Picking.objects.filter(
                order_reference__iexact=order_ref,
                sku__iexact=product.sku,
            ).values_list("quantity", flat=True)
        )
        packed_qty = sum(
            Packing.objects.filter(
                order_ref__iexact=order_ref,
                product=product,
            ).values_list("quantity", flat=True)
        )

        if picked_qty == 0:
            form.add_error("order_ref", "No picking task exists for this order and product.")
        elif packed_qty + quantity > picked_qty:
            form.add_error(
                "quantity",
                f"Only {picked_qty - packed_qty} unit(s) remain to be packed for this order.",
            )
        else:
            data = form.save()
            WarehouseActivity.objects.create(
                activity_type="PACKING",
                reference=f"PK-{data.order_ref}",
                status="COMPLETED",
            )
            messages.success(request, "Packing completed successfully.")
            return redirect("packing")

    records = Packing.objects.select_related("product").all().order_by("-created_at")
    return render(request, "accounts/packing.html", {"form": form, "records": records})


# =========================
# SHIPPING
# =========================

@login_required(login_url="login")
def shipping_page(request):
    form = ShippingForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order_ref = form.cleaned_data["order_ref"].strip()
        product = form.cleaned_data["product"]
        quantity = form.cleaned_data["quantity"]

        packed_qty = sum(
            Packing.objects.filter(
                order_ref__iexact=order_ref,
                product=product,
            ).values_list("quantity", flat=True)
        )
        shipped_qty = sum(
            Shipping.objects.filter(
                order_ref__iexact=order_ref,
                product=product,
            ).values_list("quantity", flat=True)
        )

        if packed_qty == 0:
            form.add_error("order_ref", "This order has not been packed yet.")
        elif shipped_qty + quantity > packed_qty:
            form.add_error(
                "quantity",
                f"Only {packed_qty - shipped_qty} packed unit(s) remain to ship.",
            )
        else:
            data = form.save()
            WarehouseActivity.objects.create(
                activity_type="SHIPPING",
                reference=f"SHP-{data.order_ref}",
                status="COMPLETED",
            )
            messages.success(request, "Shipment created successfully.")
            return redirect("shipping")

    records = Shipping.objects.select_related("product").all().order_by("-shipped_at")
    return render(request, "accounts/shipping.html", {"form": form, "records": records})
