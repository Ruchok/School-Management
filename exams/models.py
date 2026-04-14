from django.db import models

from academics.models import SchoolClass, StudentProfile


class Exam(models.Model):
	title = models.CharField(max_length=100)
	classroom = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exams")
	exam_date = models.DateField()
	total_marks = models.PositiveIntegerField(default=100)

	class Meta:
		ordering = ["-exam_date"]

	def __str__(self):
		return f"{self.title} - {self.classroom}"


class ExamResult(models.Model):
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="exam_results")
	marks = models.DecimalField(max_digits=5, decimal_places=2)
	grade = models.CharField(max_length=2, blank=True)

	class Meta:
		unique_together = ("exam", "student")

	def save(self, *args, **kwargs):
		percentage = float(self.marks) / max(self.exam.total_marks, 1) * 100
		if percentage >= 80:
			self.grade = "A+"
		elif percentage >= 70:
			self.grade = "A"
		elif percentage >= 60:
			self.grade = "B"
		elif percentage >= 50:
			self.grade = "C"
		else:
			self.grade = "F"
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.student} - {self.exam}"
