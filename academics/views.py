from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Q

from .forms import SchoolClassForm, StudentCreateForm, SubjectForm
from .models import SchoolClass, StudentProfile, Subject, TeacherProfile


class ClassListCreateView(LoginRequiredMixin, View):
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


class SubjectListCreateView(LoginRequiredMixin, View):
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


class StudentListCreateView(LoginRequiredMixin, View):
	template_name = "academics/students.html"

	def get(self, request):
		form = StudentCreateForm()
		students = StudentProfile.objects.select_related("user", "classroom")
		return render(request, self.template_name, {"form": form, "students": students})

	def post(self, request):
		form = StudentCreateForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("academics:students")
		students = StudentProfile.objects.select_related("user", "classroom")
		return render(request, self.template_name, {"form": form, "students": students})


class StudentSearchView(LoginRequiredMixin, View):
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
		
		return render(request, self.template_name, {
			"query": query,
			"results": results,
			"count": results.count()
		})


class TeacherListCreateView(LoginRequiredMixin, View):
	template_name = "academics/teachers.html"

	def get(self, request):
		teachers = TeacherProfile.objects.select_related("user")
		return render(request, self.template_name, {"teachers": teachers})


class TeacherSearchView(LoginRequiredMixin, View):
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
