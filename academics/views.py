from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Q

from .forms import SchoolClassForm, StudentCreateForm, SubjectForm
from .models import SchoolClass, StudentProfile, Subject, TeacherProfile
from school_admin.models import ClassRoutine


class NonStudentRequiredMixin:
	"""Mixin to prevent students from accessing teacher/admin views"""
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated and request.user.role == 'STUDENT':
			return redirect('home')
		return super().dispatch(request, *args, **kwargs)


class ClassListCreateView(NonStudentRequiredMixin, LoginRequiredMixin, View):
	template_name = "academics/classes.html"

	def get(self, request):
		form = SchoolClassForm()
		classes = SchoolClass.objects.select_related("class_teacher")
		return render(request, self.template_name, {"form": form, "classes": classes})

	def post(self, request):
		form = SchoolClassForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("academics:classes")
		classes = SchoolClass.objects.select_related("class_teacher")
		return render(request, self.template_name, {"form": form, "classes": classes})


class SubjectListCreateView(NonStudentRequiredMixin, LoginRequiredMixin, View):
	template_name = "academics/subjects.html"

	def get(self, request):
		form = SubjectForm()
		subjects = Subject.objects.select_related("classroom", "teacher")
		return render(request, self.template_name, {"form": form, "subjects": subjects})

	def post(self, request):
		form = SubjectForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("academics:subjects")
		subjects = Subject.objects.select_related("classroom", "teacher")
		return render(request, self.template_name, {"form": form, "subjects": subjects})


class StudentListCreateView(NonStudentRequiredMixin, LoginRequiredMixin, View):
	template_name = "academics/students.html"

	def get(self, request):
		return render(request, self.template_name)


class StudentSearchView(NonStudentRequiredMixin, LoginRequiredMixin, View):
	template_name = "academics/search.html"

	def get(self, request):
		query = request.GET.get('q', '')
		results = []
		
		if query:
			results = StudentProfile.objects.select_related("user", "classroom").filter(
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query) |
				Q(user__email__icontains=query) |
				Q(roll_number__icontains=query) |
				Q(classroom__name__icontains=query)
			)
			
			# Add routine information to each student
			for student in results:
				student.routine = ClassRoutine.objects.filter(
					classroom=student.classroom
				).select_related('subject', 'teacher__user').order_by('day_of_week', 'start_time')
		
		return render(request, self.template_name, {
			"query": query,
			"results": results,
			"count": results.count()
		})


class TeacherListCreateView(NonStudentRequiredMixin, LoginRequiredMixin, View):
	template_name = "academics/teachers.html"

	def get(self, request):
		teachers = TeacherProfile.objects.select_related("user")
		return render(request, self.template_name, {"teachers": teachers})


class TeacherSearchView(NonStudentRequiredMixin, LoginRequiredMixin, View):
	template_name = "academics/teacher_search.html"

	def get(self, request):
		query = request.GET.get('q', '')
		results = []
		
		if query:
			results = TeacherProfile.objects.select_related("user").filter(
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query) |
				Q(user__email__icontains=query) |
				Q(subject_expertise__icontains=query) |
				Q(qualification__icontains=query)
			)
		
		return render(request, self.template_name, {
			"query": query,
			"results": results,
			"count": results.count()
		})


class StudentTeacherSearchView(LoginRequiredMixin, View):
	"""Search view for students to find and contact teachers.
	Only students can access this view."""
	template_name = "academics/student_teacher_search.html"
	login_url = '/login/student/'

	def dispatch(self, request, *args, **kwargs):
		# Only allow students to access this view
		if request.user.role != 'STUDENT':
			return redirect('home')
		return super().dispatch(request, *args, **kwargs)

	def get(self, request):
		query = request.GET.get('q', '')
		results = []
		teachers_list = []
		
		# Get all teachers with their subjects
		all_teachers = TeacherProfile.objects.select_related("user").prefetch_related(
			'user__subjects'
		)
		
		# If search query exists, filter teachers
		if query:
			results = all_teachers.filter(
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query) |
				Q(user__email__icontains=query) |
				Q(qualification__icontains=query)
			)
		else:
			# Show all teachers if no query
			results = all_teachers
		
		# Build enhanced teacher list with their subjects
		for teacher in results:
			teacher_data = {
				'profile': teacher,
				'subjects': Subject.objects.filter(teacher=teacher.user),
			}
			teachers_list.append(teacher_data)
		
		return render(request, self.template_name, {
			"query": query,
			"results": teachers_list,
			"count": len(teachers_list),
			"total_teachers": all_teachers.count(),
		})
