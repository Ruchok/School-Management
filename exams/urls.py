from django.urls import path

from .views import ExamListCreateView, ExamResultListCreateView

app_name = "exams"

urlpatterns = [
    path("", ExamListCreateView.as_view(), name="list"),
    path("results/", ExamResultListCreateView.as_view(), name="results"),
]
