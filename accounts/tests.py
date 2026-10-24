from django.contrib.auth.models import User
from django.db.models import Sum
from django.test import TestCase

from .models import Packing, Picking, Product, Putaway, Receiving, Shipping


class ReceivingPutawayInventoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="warehouse-user", password="test-password")
        self.client.force_login(self.user)

    def receive_goods(self, **overrides):
        data = {
            "product_name": "Pallet Jack",
            "sku": "PJ-100",
            "quantity": 4,
            "unit_price": "25.00",
            "supplier": "Warehouse Supplier",
            "condition": Receiving.CONDITION_GOOD,
        }
        data.update(overrides)
        return self.client.post("/receiving/", data)

    def test_good_receiving_updates_inventory_only_after_putaway(self):
        response = self.receive_goods()

        self.assertRedirects(response, "/receiving/")
        receiving = Receiving.objects.get(sku="PJ-100")
        self.assertFalse(Product.objects.filter(sku="PJ-100").exists())

        putaway_response = self.client.post(
            "/putaway/",
            {"receiving": receiving.pk, "location": "A-01"},
        )

        self.assertRedirects(putaway_response, "/putaway/")
        receiving.refresh_from_db()
        product = Product.objects.get(sku="PJ-100")
        self.assertEqual(product.name, "Pallet Jack")
        self.assertEqual(product.quantity, 4)
        self.assertEqual(receiving.status, "STORED")
        self.assertTrue(receiving.inventory_updated)
        self.assertTrue(Putaway.objects.filter(receiving=receiving).exists())

    def test_putaway_choices_only_include_good_received_goods(self):
        good_receiving = Receiving.objects.create(
            product_name="Pallet Jack",
            sku="PJ-100",
            quantity=4,
            unit_price="25.00",
            supplier="Warehouse Supplier",
        )
        damaged_receiving = Receiving.objects.create(
            product_name="Damaged Pallet Jack",
            sku="PJ-200",
            quantity=2,
            unit_price="25.00",
            supplier="Warehouse Supplier",
            condition=Receiving.CONDITION_DAMAGED,
        )

        response = self.client.get("/putaway/")

        self.assertContains(response, "Pallet Jack — SKU PJ-100 — Qty 4")
        self.assertNotContains(response, "Damaged Pallet Jack")
        self.assertIn(good_receiving, response.context["form"].fields["receiving"].queryset)
        self.assertNotIn(damaged_receiving, response.context["form"].fields["receiving"].queryset)

    def test_inventory_page_has_no_manual_product_entry_form(self):
        response = self.client.get("/inventory/")

        self.assertContains(response, "All Products")
        self.assertNotContains(response, "Add New Product")
        self.assertNotContains(response, "Save Product")

    def test_picking_selects_inventory_product_and_uses_its_name_and_sku(self):
        product = Product.objects.create(
            name="Pallet Jack",
            sku="PJ-100",
            quantity=8,
        )
        out_of_stock = Product.objects.create(
            name="Empty Pallet Jack",
            sku="PJ-000",
            quantity=0,
        )

        response = self.client.get("/picking/")

        self.assertContains(response, "Pallet Jack — SKU PJ-100 — Available: 8")
        self.assertNotContains(response, "Empty Pallet Jack")
        self.assertIn(product, response.context["form"].fields["product"].queryset)
        self.assertNotIn(out_of_stock, response.context["form"].fields["product"].queryset)

        post_response = self.client.post(
            "/picking/",
            {"product": product.pk, "quantity": 3, "order_reference": "ORD-2001"},
        )

        self.assertRedirects(post_response, "/picking/")
        product.refresh_from_db()
        picking = Picking.objects.get(order_reference="ORD-2001")
        self.assertEqual(picking.product_name, "Pallet Jack")
        self.assertEqual(picking.sku, "PJ-100")
        self.assertEqual(picking.quantity, 3)
        self.assertEqual(product.quantity, 5)

    def test_picking_rejects_product_not_in_inventory_choices(self):
        product = Product.objects.create(
            name="Pallet Jack",
            sku="PJ-100",
            quantity=0,
        )

        response = self.client.post(
            "/picking/",
            {"product": product.pk, "quantity": 1, "order_reference": "ORD-2002"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Picking.objects.filter(order_reference="ORD-2002").exists())

    def test_packing_choices_only_include_picked_products_with_remaining_quantity(self):
        product = Product.objects.create(name="Pallet Jack", sku="PJ-100", quantity=5)
        other_product = Product.objects.create(name="Forklift", sku="FL-200", quantity=5)
        Picking.objects.create(
            product_name=product.name,
            sku=product.sku,
            quantity=5,
            order_reference="ORD-3001",
        )
        Picking.objects.create(
            product_name=other_product.name,
            sku=other_product.sku,
            quantity=2,
            order_reference="ORD-3002",
        )
        Packing.objects.create(order_ref="ORD-3001", product=product, quantity=3)

        response = self.client.get("/packing/")
        form = response.context["form"]

        self.assertEqual(
            form.fields["order_ref"].choices[1:],
            [("ORD-3001", "ORD-3001"), ("ORD-3002", "ORD-3002")],
        )
        self.assertEqual(list(form.fields["product"].queryset), [])

        response = self.client.get("/packing/?order_ref=ORD-3001")
        form = response.context["form"]
        self.assertEqual(list(form.fields["product"].queryset), [product])
        self.assertContains(response, "Remaining to pack: 2")

        response = self.client.post(
            "/packing/",
            {"order_ref": "ORD-3001", "product": product.pk, "quantity": 2},
        )

        self.assertRedirects(response, "/packing/")
        self.assertEqual(Packing.objects.filter(order_ref="ORD-3001").aggregate(total=Sum("quantity"))["total"], 5)

    def test_shipping_choices_only_include_packed_products_with_remaining_quantity(self):
        product = Product.objects.create(name="Pallet Jack", sku="PJ-100", quantity=0)
        Packing.objects.create(order_ref="ORD-4001", product=product, quantity=4)
        Shipping.objects.create(
            order_ref="ORD-4001",
            product=product,
            quantity=1,
            destination="Customer",
        )

        response = self.client.get("/shipping/?order_ref=ORD-4001")
        form = response.context["form"]
        self.assertEqual(list(form.fields["product"].queryset), [product])
        self.assertContains(response, "Remaining to ship: 3")

        response = self.client.post(
            "/shipping/",
            {
                "order_ref": "ORD-4001",
                "product": product.pk,
                "quantity": 3,
                "destination": "Customer",
            },
        )

        self.assertRedirects(response, "/shipping/")
        self.assertEqual(Shipping.objects.filter(order_ref="ORD-4001").aggregate(total=Sum("quantity"))["total"], 4)
