from django import forms
from .models import Packing, Picking, Product, Putaway, Receiving, Shipping


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "quantity"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Product name"}),
            "sku": forms.TextInput(attrs={"placeholder": "SKU"}),
            "quantity": forms.NumberInput(attrs={"min": 0, "placeholder": "Quantity"}),
        }

    def clean_quantity(self):
        value = self.cleaned_data["quantity"]
        if value < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return value


class ReceivingForm(StyledModelForm):
    class Meta:
        model = Receiving
        fields = [
            "product_name", "sku", "quantity", "unit_price",
            "supplier", "expiry_date", "condition",
        ]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "unit_price": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_quantity(self):
        value = self.cleaned_data["quantity"]
        if value <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return value

    def clean_unit_price(self):
        value = self.cleaned_data["unit_price"]
        if value < 0:
            raise forms.ValidationError("Unit price cannot be negative.")
        return value


class PutawayForm(StyledModelForm):
    class Meta:
        model = Putaway
        fields = ["receiving", "location"]

    def clean_location(self):
        value = self.cleaned_data["location"].strip()
        if not value:
            raise forms.ValidationError("Storage location is required.")
        return value


class PickingForm(StyledModelForm):
    class Meta:
        model = Picking
        fields = ["product_name", "sku", "quantity", "order_reference"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "order_reference": forms.TextInput(attrs={"placeholder": "e.g. ORD-1001"}),
        }

    def clean_quantity(self):
        value = self.cleaned_data["quantity"]
        if value <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return value


class PackingForm(StyledModelForm):
    class Meta:
        model = Packing
        fields = ["order_ref", "product", "quantity"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
        }

    def clean_quantity(self):
        value = self.cleaned_data["quantity"]
        if value <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return value


class ShippingForm(StyledModelForm):
    class Meta:
        model = Shipping
        fields = ["order_ref", "product", "quantity", "destination"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "destination": forms.TextInput(attrs={"placeholder": "Customer / delivery address"}),
        }

    def clean_quantity(self):
        value = self.cleaned_data["quantity"]
        if value <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return value

    def clean_destination(self):
        value = self.cleaned_data["destination"].strip()
        if not value:
            raise forms.ValidationError("Destination is required.")
        return value
