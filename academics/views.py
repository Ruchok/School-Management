from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import SchoolClassForm, StudentCreateForm, SubjectForm
from .models import SchoolClass, StudentProfile, Subject


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
