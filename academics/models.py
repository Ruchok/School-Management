from django.conf import settings
from django.db import models


class SchoolClass(models.Model):
	name = models.CharField(max_length=50)
	section = models.CharField(max_length=10)
	class_teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="managed_classes",
	)

	class Meta:
		unique_together = ("name", "section")
		ordering = ["name", "section"]

	def __str__(self):
		return f"{self.name} - {self.section}"


class TeacherProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	qualification = models.CharField(max_length=120, blank=True)
	specialization = models.CharField(max_length=120, blank=True)
	joined_on = models.DateField(null=True, blank=True)

	def __str__(self):
		return self.user.get_full_name() or self.user.username


class Subject(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=20, unique=True)
	classroom = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="subjects")
	teacher = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="subjects",
	)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return f"{self.name} ({self.code})"


class StudentProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	classroom = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
	roll_number = models.CharField(max_length=20, unique=True)
	admission_date = models.DateField()
	guardian_name = models.CharField(max_length=120)
	guardian_phone = models.CharField(max_length=20)

	class Meta:
		ordering = ["roll_number"]

	def __str__(self):
		return f"{self.roll_number} - {self.user.get_full_name() or self.user.username}"
