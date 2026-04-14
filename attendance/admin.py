from django.contrib import admin

from .models import Attendance, AttendanceRecord


class AttendanceRecordInline(admin.TabularInline):
	model = AttendanceRecord
	extra = 0


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ("classroom", "date", "taken_by")
	list_filter = ("classroom", "date")
	inlines = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
	list_display = ("attendance", "student", "status")
	list_filter = ("status", "attendance__date")
	search_fields = ("student__roll_number", "student__user__username")

# Register your models here.
