from django.conf import settings
from django.db import models

from academics.models import SchoolClass, StudentProfile


class FeeStructure(models.Model):
	title = models.CharField(max_length=100)
	classroom = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="fee_structures")
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	due_date = models.DateField()

	def __str__(self):
		return f"{self.title} - {self.classroom}"


class FeeInvoice(models.Model):
	class Status(models.TextChoices):
		PENDING = "PENDING", "Pending"
		PARTIAL = "PARTIAL", "Partial"
		PAID = "PAID", "Paid"

	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="invoices")
	fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="invoices")
	amount_due = models.DecimalField(max_digits=10, decimal_places=2)
	amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	issued_on = models.DateField(auto_now_add=True)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

	def save(self, *args, **kwargs):
		if self.amount_paid <= 0:
			self.status = self.Status.PENDING
		elif self.amount_paid < self.amount_due:
			self.status = self.Status.PARTIAL
		else:
			self.status = self.Status.PAID
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.student} - {self.fee_structure}"


class FeePayment(models.Model):
	class Method(models.TextChoices):
		CASH = "CASH", "Cash"
		BANK = "BANK", "Bank"
		MOBILE = "MOBILE", "Mobile Banking"

	invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="payments")
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	payment_date = models.DateField(auto_now_add=True)
	method = models.CharField(max_length=10, choices=Method.choices, default=Method.CASH)
	received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return f"{self.invoice} - {self.amount}"
