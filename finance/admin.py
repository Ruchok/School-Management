from django.contrib import admin

from .models import FeeInvoice, FeePayment, FeeStructure


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
	list_display = ("title", "classroom", "amount", "due_date")
	list_filter = ("classroom",)


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
	list_display = ("student", "fee_structure", "amount_due", "amount_paid", "status")
	list_filter = ("status", "fee_structure__classroom")


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
	list_display = ("invoice", "amount", "method", "payment_date", "received_by")
	list_filter = ("method", "payment_date")

# Register your models here.
