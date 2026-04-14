from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from academics.models import StudentProfile

from .forms import AttendanceBulkForm
from .models import Attendance, AttendanceRecord


class AttendanceListView(LoginRequiredMixin, View):
	template_name = "attendance/list.html"

	def get(self, request):
		selected_classroom = request.GET.get("classroom")
		students = StudentProfile.objects.none()
		if selected_classroom:
			students = StudentProfile.objects.filter(classroom_id=selected_classroom).select_related("user")
		records = Attendance.objects.select_related("classroom", "taken_by")[:30]
		return render(
			request,
			self.template_name,
			{
				"attendance_days": records,
				"form": AttendanceBulkForm(initial={"classroom": selected_classroom}),
				"students": students,
			},
		)

	def post(self, request):
		form = AttendanceBulkForm(request.POST)
		if not form.is_valid():
			records = Attendance.objects.select_related("classroom", "taken_by")[:30]
			return render(request, self.template_name, {"attendance_days": records, "form": form})

		classroom = form.cleaned_data["classroom"]
		date = form.cleaned_data["date"]
		attendance, _ = Attendance.objects.get_or_create(
			classroom=classroom,
			date=date,
			defaults={"taken_by": request.user},
		)

		students = StudentProfile.objects.filter(classroom=classroom)
		for student in students:
			status = request.POST.get(f"status_{student.id}", AttendanceRecord.Status.PRESENT)
			AttendanceRecord.objects.update_or_create(
				attendance=attendance,
				student=student,
				defaults={"status": status},
			)

		messages.success(request, "Attendance saved successfully.")
		return redirect("attendance:list")
