from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import ExamForm, ExamResultForm
from .models import Exam, ExamResult


class ExamListCreateView(LoginRequiredMixin, View):
	template_name = "exams/exams.html"

	def get(self, request):
		form = ExamForm()
		exams = Exam.objects.select_related("classroom")[:30]
		return render(request, self.template_name, {"form": form, "exams": exams})

	def post(self, request):
		form = ExamForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("exams:list")
		exams = Exam.objects.select_related("classroom")[:30]
		return render(request, self.template_name, {"form": form, "exams": exams})


class ExamResultListCreateView(LoginRequiredMixin, View):
	template_name = "exams/results.html"

	def get(self, request):
		form = ExamResultForm()
		results = ExamResult.objects.select_related("exam", "student__user")[:40]
		return render(request, self.template_name, {"form": form, "results": results})

	def post(self, request):
		form = ExamResultForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect("exams:results")
		results = ExamResult.objects.select_related("exam", "student__user")[:40]
		return render(request, self.template_name, {"form": form, "results": results})
