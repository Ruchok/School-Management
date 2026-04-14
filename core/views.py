from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import RedirectView, TemplateView

from academics.models import SchoolClass, StudentProfile, Subject
from attendance.models import AttendanceRecord
from exams.models import Exam, ExamResult
from finance.models import FeeInvoice, FeePayment


class HomeRedirectView(RedirectView):
	pattern_name = "dashboard"


class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = "core/dashboard.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["stats"] = {
			"students": StudentProfile.objects.count(),
			"classes": SchoolClass.objects.count(),
			"subjects": Subject.objects.count(),
			"exams": Exam.objects.count(),
			"results": ExamResult.objects.count(),
			"invoices": FeeInvoice.objects.count(),
			"payments": FeePayment.objects.count(),
		}
		context["attendance_breakdown"] = AttendanceRecord.objects.values("status").annotate(total=Count("id"))
		context["recent_students"] = StudentProfile.objects.select_related("user", "classroom")[:6]
		context["recent_invoices"] = FeeInvoice.objects.select_related("student__user")[:6]
		return context
