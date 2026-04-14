from django.contrib import admin

from .models import Exam, ExamResult


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
	list_display = ("title", "classroom", "exam_date", "total_marks")
	list_filter = ("classroom", "exam_date")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
	list_display = ("exam", "student", "marks", "grade")
	list_filter = ("exam", "grade")
	search_fields = ("student__roll_number", "student__user__username")

# Register your models here.
