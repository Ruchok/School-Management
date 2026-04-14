from django.urls import path

from .views import FeeStructureListCreateView, InvoiceListCreateView, PaymentListCreateView

app_name = "finance"

urlpatterns = [
    path("structures/", FeeStructureListCreateView.as_view(), name="structures"),
    path("invoices/", InvoiceListCreateView.as_view(), name="invoices"),
    path("payments/", PaymentListCreateView.as_view(), name="payments"),
]
