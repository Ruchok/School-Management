from django.contrib import admin

from .models import SchoolClass, StudentProfile, Subject, TeacherProfile


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
	list_display = ("name", "section", "class_teacher")
	search_fields = ("name", "section")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "qualification", "specialization", "joined_on")
	search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ("name", "code", "classroom", "teacher")
	list_filter = ("classroom",)
	search_fields = ("name", "code")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("roll_number", "user", "classroom", "admission_date")
	list_filter = ("classroom",)
	search_fields = ("roll_number", "user__username", "user__first_name", "user__last_name")

# Register your models here.
