from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import FeeInvoiceForm, FeePaymentForm, FeeStructureForm
from .models import FeeInvoice, FeePayment, FeeStructure


class FeeStructureListCreateView(LoginRequiredMixin, View):
	template_name = "finance/structures.html"

	def get(self, request):
		form = FeeStructureForm()
		structures = FeeStructure.objects.select_related("classroom")[:30]
		return render(request, self.template_name, {"form": form, "structures": structures})

	def post(self, request):
		form = FeeStructureForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("finance:structures")
		structures = FeeStructure.objects.select_related("classroom")[:30]
		return render(request, self.template_name, {"form": form, "structures": structures})


class InvoiceListCreateView(LoginRequiredMixin, View):
	template_name = "finance/invoices.html"

	def get(self, request):
		form = FeeInvoiceForm()
		invoices = FeeInvoice.objects.select_related("student__user", "fee_structure")[:40]
		return render(request, self.template_name, {"form": form, "invoices": invoices})

	def post(self, request):
		form = FeeInvoiceForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("finance:invoices")
		invoices = FeeInvoice.objects.select_related("student__user", "fee_structure")[:40]
		return render(request, self.template_name, {"form": form, "invoices": invoices})


class PaymentListCreateView(LoginRequiredMixin, View):
	template_name = "finance/payments.html"

	def get(self, request):
		form = FeePaymentForm()
		payments = FeePayment.objects.select_related("invoice__student__user")[:40]
		return render(request, self.template_name, {"form": form, "payments": payments})

	def post(self, request):
		form = FeePaymentForm(request.POST)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.received_by = request.user
			payment.save()

			invoice = payment.invoice
			invoice.amount_paid += payment.amount
			invoice.save()

			return redirect("finance:payments")
		payments = FeePayment.objects.select_related("invoice__student__user")[:40]
		return render(request, self.template_name, {"form": form, "payments": payments})
