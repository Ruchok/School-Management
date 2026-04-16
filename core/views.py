from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import authenticate, login
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from academics.models import SchoolClass, StudentProfile, Subject, TeacherProfile
from attendance.models import AttendanceRecord
from exams.models import Exam, ExamResult
from finance.models import FeeInvoice, FeePayment
from users.models import CustomUser


class HomeRedirectView(RedirectView):
	def get_redirect_url(self, *args, **kwargs):
		if self.request.user.is_authenticated:
			return "/dashboard/"
		return "/login/"


class LoginView(View):
	"""Custom login view for CustomUser model"""
	template_name = 'auth/login.html'
	
	def get(self, request):
		if request.user.is_authenticated:
			return redirect('dashboard')
		return render(request, self.template_name)
	
	def post(self, request):
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		user = authenticate(request, username=username, password=password)
		
		if user is not None:
			login(request, user)
			messages.success(request, f'Welcome back, {user.first_name or user.username}!')
			return redirect('dashboard')
		else:
			messages.error(request, 'Invalid username or password. Please try again.')
			return render(request, self.template_name, {
				'username': username,
			})


class DashboardView(LoginRequiredMixin, TemplateView):
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

		if user.role == "ADMIN":
			context.update(self._admin_context())
		elif user.role == "TEACHER":
			context.update(self._teacher_context(user))
		elif user.role == "STUDENT":
			context.update(self._student_context(user))
		elif user.role == "ACCOUNTANT":
			context.update(self._accountant_context())

		return context

	def _admin_context(self):
		"""Admin dashboard shows overall system statistics"""
		return {
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
