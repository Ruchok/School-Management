from django.db import models
from academics.models import SchoolClass, Subject, TeacherProfile


class ClassRoutine(models.Model):
    """Class schedule/routine management"""
    classroom = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='routines')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    room_number = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['classroom', 'day_of_week', 'start_time']
        unique_together = ['classroom', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.classroom} - {self.subject} ({self.day_of_week})"
