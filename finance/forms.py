from django import forms

from .models import FeeInvoice, FeePayment, FeeStructure


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ["title", "classroom", "amount", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class FeeInvoiceForm(forms.ModelForm):
    class Meta:
        model = FeeInvoice
        fields = ["student", "fee_structure", "amount_due", "amount_paid"]


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ["invoice", "amount", "method"]
