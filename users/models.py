from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
	class Roles(models.TextChoices):
		ADMIN = "ADMIN", "Admin"
		TEACHER = "TEACHER", "Teacher"
		STUDENT = "STUDENT", "Student"
		ACCOUNTANT = "ACCOUNTANT", "Accountant"

	role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
	phone = models.CharField(max_length=20, blank=True)
	avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

	def __str__(self):
		return f"{self.get_full_name() or self.username} ({self.role})"
