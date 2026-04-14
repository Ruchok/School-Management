from django.conf import settings
from django.db import models

from academics.models import SchoolClass, StudentProfile


class Attendance(models.Model):
	classroom = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="attendance_days")
	date = models.DateField()
	taken_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	notes = models.CharField(max_length=255, blank=True)

	class Meta:
		unique_together = ("classroom", "date")
		ordering = ["-date"]

	def __str__(self):
		return f"{self.classroom} - {self.date}"


class AttendanceRecord(models.Model):
	class Status(models.TextChoices):
		PRESENT = "PRESENT", "Present"
		ABSENT = "ABSENT", "Absent"
		LATE = "LATE", "Late"

	attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="records")
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="attendance_records")
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)

	class Meta:
		unique_together = ("attendance", "student")

	def __str__(self):
		return f"{self.student} - {self.status}"
