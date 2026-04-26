from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import authenticate, login
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.middleware.csrf import get_token

from academics.models import SchoolClass, StudentProfile, Subject, TeacherProfile
from attendance.models import AttendanceRecord
from exams.models import Exam, ExamResult
from finance.models import FeeInvoice, FeePayment
from users.models import CustomUser


def _role_home_url(user):
	"""Return the appropriate home URL for an authenticated user's role."""
	if user.role in ("ADMIN", "PRINCIPLE_ADMIN") or user.is_staff or user.is_superuser:
		return "/school-admin/dashboard/"
	return "/dashboard/"


class HomePageView(TemplateView):
	"""Home/Landing page - shows login options for unauthenticated, redirects authenticated users."""
	template_name = 'landing.html'

	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect(_role_home_url(request.user))
		return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Base role-gated login view
# ---------------------------------------------------------------------------

class _RoleLoginView(View):
	"""Shared login logic; subclasses set `allowed_roles`, `template_name`,
	and `role_label` for the context.
	Set `allow_staff = True` only on portals that accept admin/staff accounts."""
	allowed_roles = []
	allow_staff = False       # staff/superusers are blocked by default
	template_name = 'auth/login.html'
	role_label = 'User'

	def _already_logged_in_redirect(self, request):
		return redirect(_role_home_url(request.user))

	def get(self, request):
		if request.user.is_authenticated:
			return self._already_logged_in_redirect(request)
		return render(request, self.template_name, {'role_label': self.role_label})

	def post(self, request):
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '')

		user = authenticate(request, username=username, password=password)

		if user is None:
			messages.error(request, 'Invalid username or password.')
			return render(request, self.template_name, {
				'username': username,
				'role_label': self.role_label,
			})

		# Staff / superuser accounts must use the School Admin portal only
		if not self.allow_staff and (user.is_staff or user.is_superuser):
			messages.error(
				request,
				'Administrator accounts must use the School Admin portal at /school-admin/login/'
			)
			return render(request, self.template_name, {
				'username': username,
				'role_label': self.role_label,
			})

		# Role must exactly match the portal's allowed roles
		if self.allowed_roles and user.role not in self.allowed_roles:
			messages.error(
				request,
				f'This portal is for {self.role_label} accounts only. '
				f'Your account role is "{user.get_role_display()}". '
				f'Please use the correct login portal.'
			)
			return render(request, self.template_name, {
				'username': username,
				'role_label': self.role_label,
			})

		login(request, user)
		messages.success(request, f'Welcome back, {user.first_name or user.username}!')
		return redirect(_role_home_url(user))


class LoginView(_RoleLoginView):
	"""General fallback login — accepts any role but still blocks
	staff/superusers and directs them to the correct portal."""
	allowed_roles = []
	allow_staff = False
	template_name = 'auth/login.html'
	role_label = 'User'


class StudentLoginView(_RoleLoginView):
	allowed_roles = [CustomUser.Roles.STUDENT]
	template_name = 'auth/login_student.html'
	role_label = 'Student'


class TeacherLoginView(_RoleLoginView):
	allowed_roles = [CustomUser.Roles.TEACHER]
	template_name = 'auth/login_teacher.html'
	role_label = 'Teacher'


class AccountantLoginView(_RoleLoginView):
	allowed_roles = [CustomUser.Roles.ACCOUNTANT]
	template_name = 'auth/login_accountant.html'
	role_label = 'Accountant'


class DashboardView(LoginRequiredMixin, TemplateView):
	login_url = '/'

	def dispatch(self, request, *args, **kwargs):
		# School admins / superusers belong in the school-admin panel, not here
		if request.user.is_authenticated and (
			request.user.role in ("ADMIN", "PRINCIPLE_ADMIN")
			or request.user.is_staff
			or request.user.is_superuser
		):
			return redirect('school_admin:dashboard')
		return super().dispatch(request, *args, **kwargs)

	def get_template_names(self):
		user = self.request.user
		if user.role == "ADMIN":
			return ["core/admin_dashboard.html"]
		elif user.role == "TEACHER":
			return ["core/teacher_dashboard.html"]
		elif user.role == "STUDENT":
			return ["core/student_dashboard.html"]
		elif user.role == "ACCOUNTANT":
			return ["core/accountant_dashboard.html"]
		return ["core/dashboard.html"]

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		
		# Always include user in context
		context['user'] = user

		if user.role == "ADMIN":
			context.update(self._admin_context())
		elif user.role == "TEACHER":
			context.update(self._teacher_context(user))
		elif user.role == "STUDENT":
			context.update(self._student_context(user))
		elif user.role == "ACCOUNTANT":
			context.update(self._accountant_context())

		# Ensure user is always in context (in case context.update overwrote it)
		context['user'] = user
		
		return context

	def _admin_context(self):
		"""Admin dashboard shows overall system statistics"""
		return {
			"user": self.request.user,
			"stats": {
				"students": StudentProfile.objects.count(),
				"teachers": CustomUser.objects.filter(role="TEACHER").count(),
				"classes": SchoolClass.objects.count(),
				"subjects": Subject.objects.count(),
				"exams": Exam.objects.count(),
				"results": ExamResult.objects.count(),
				"invoices": FeeInvoice.objects.count(),
				"payments": FeePayment.objects.count(),
				"users": CustomUser.objects.count(),
				"accountants": CustomUser.objects.filter(role="ACCOUNTANT").count(),
			},
			"attendance_breakdown": AttendanceRecord.objects.values("status").annotate(total=Count("id")),
			"recent_students": StudentProfile.objects.select_related("user", "classroom")[:6],
			"recent_invoices": FeeInvoice.objects.select_related("student__user")[:6],
			"recent_exams": Exam.objects.order_by("-exam_date")[:5],
			"classes_list": SchoolClass.objects.all(),
		}

	def _teacher_context(self, user):
		"""Teacher dashboard shows their classes and students"""
		try:
			teacher_profile = TeacherProfile.objects.get(user=user)
		except TeacherProfile.DoesNotExist:
			teacher_profile = None

		# Classes managed by this teacher
		managed_classes = SchoolClass.objects.filter(class_teacher=user)
		
		# Subjects taught by this teacher
		subjects = Subject.objects.filter(teacher=user)

		# All students in their classes
		students = StudentProfile.objects.filter(classroom__in=managed_classes)

		# Attendance data for their classes
		attendance_data = AttendanceRecord.objects.filter(
			student__classroom__in=managed_classes
		).values("status").annotate(total=Count("id"))

		# Recent exams for their classes
		exams = Exam.objects.filter(classroom__in=managed_classes).order_by("-exam_date")[:5]

		return {
			"user": user,
			"teacher_profile": teacher_profile,
			"managed_classes": managed_classes,
			"subjects": subjects,
			"stats": {
				"classes": managed_classes.count(),
				"subjects": subjects.count(),
				"students": students.count(),
				"exams": exams.count(),
			},
			"attendance_breakdown": attendance_data,
			"recent_students": students[:6],
			"recent_exams": exams,
		}

	def _student_context(self, user):
		"""Student dashboard shows their personal information and progress"""
		try:
			student_profile = StudentProfile.objects.get(user=user)
		except StudentProfile.DoesNotExist:
			return {
				"message": "Your student profile is not set up yet. Please contact administration.",
				"user": user,
			}

		classroom = student_profile.classroom

		# Get subjects for student's class
		subjects = Subject.objects.filter(classroom=classroom) if classroom else []

		# Get exams for student's class
		exams = Exam.objects.filter(classroom=classroom).order_by("-exam_date") if classroom else []

		# Get exam results
		exam_results = ExamResult.objects.filter(student=student_profile).select_related("exam")

		# Get attendance records
		attendance_records = AttendanceRecord.objects.filter(
			student=student_profile
		).select_related("attendance")

		# Calculate attendance percentage
		total_attendance = attendance_records.count()
		present_count = attendance_records.filter(status="PRESENT").count()
		attendance_percentage = (
			(present_count / total_attendance * 100) if total_attendance > 0 else 0
		)

		# Get fee invoices
		invoices = FeeInvoice.objects.filter(student=student_profile)
		total_due = invoices.aggregate(Sum("amount_due"))["amount_due__sum"] or 0
		total_paid = invoices.aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0

		return {
			"user": user,
			"student_profile": student_profile,
			"classroom": classroom,
			"subjects": subjects,
			"stats": {
				"subjects": subjects.count(),
				"exams": exams.count(),
				"results": exam_results.count(),
				"attendance_percentage": round(attendance_percentage, 2),
			},
			"recent_exams": exams[:5],
			"exam_results": exam_results[:5],
			"attendance_records": attendance_records.order_by("-attendance__date")[:10],
			"invoices": invoices,
			"financial_summary": {
				"total_due": total_due,
				"total_paid": total_paid,
				"balance": total_due - total_paid,
			},
		}

	def _accountant_context(self):
		"""Accountant dashboard shows financial information"""
		invoices = FeeInvoice.objects.all()
		payments = FeePayment.objects.all()

		total_due = invoices.aggregate(Sum("amount_due"))["amount_due__sum"] or 0
		total_paid = invoices.aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0
		total_revenue = payments.aggregate(Sum("amount"))["amount__sum"] or 0

		invoice_status_breakdown = invoices.values("status").annotate(count=Count("id"))

		return {
			"user": self.request.user,
			"stats": {
				"total_invoices": invoices.count(),
				"pending_invoices": invoices.filter(status="PENDING").count(),
				"partial_invoices": invoices.filter(status="PARTIAL").count(),
				"paid_invoices": invoices.filter(status="PAID").count(),
				"total_payments": payments.count(),
			},
			"financial_summary": {
				"total_due": total_due,
				"total_paid": total_paid,
				"balance_pending": total_due - total_paid,
				"total_revenue": total_revenue,
			},
			"invoice_status_breakdown": invoice_status_breakdown,
			"recent_invoices": invoices.select_related("student__user").order_by("-issued_on")[:6],
			"recent_payments": payments.select_related("invoice__student__user").order_by("-id")[:6],
			"pending_invoices": invoices.filter(status="PENDING").select_related("student__user")[:10],
		}
