from django.urls import path

from .views import ClassListCreateView, StudentListCreateView, SubjectListCreateView

app_name = "academics"

urlpatterns = [
    path("classes/", ClassListCreateView.as_view(), name="classes"),
    path("subjects/", SubjectListCreateView.as_view(), name="subjects"),
    path("students/", StudentListCreateView.as_view(), name="students"),
]
