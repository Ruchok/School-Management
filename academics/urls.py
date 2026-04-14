from django.urls import path
from django.views.generic import TemplateView

from .views import ClassListCreateView, StudentListCreateView, SubjectListCreateView, StudentSearchView, TeacherListCreateView, TeacherSearchView
from .api_views import students_data_api, classes_data_api, subjects_data_api, attendance_data_api, exams_data_api, payments_data_api, teachers_data_api

app_name = "academics"

urlpatterns = [
    # Form-based views
    path("classes/", ClassListCreateView.as_view(), name="classes"),
    path("subjects/", SubjectListCreateView.as_view(), name="subjects"),
    path("students/", StudentListCreateView.as_view(), name="students"),
    path("search/", StudentSearchView.as_view(), name="search"),
    path("teachers/", TeacherListCreateView.as_view(), name="teachers"),
    path("teachers/search/", TeacherSearchView.as_view(), name="teachers_search"),
    
    # AG Grid views
    path("grid/students/", TemplateView.as_view(template_name="academics/students_grid.html"), name="students_grid"),
    path("grid/classes/", TemplateView.as_view(template_name="academics/classes_grid.html"), name="classes_grid"),
    path("grid/subjects/", TemplateView.as_view(template_name="academics/subjects_grid.html"), name="subjects_grid"),
    path("grid/teachers/", TemplateView.as_view(template_name="academics/teachers_grid.html"), name="teachers_grid"),
    path("grid/attendance/", TemplateView.as_view(template_name="attendance/attendance_grid.html"), name="attendance_grid"),
    path("grid/exams/", TemplateView.as_view(template_name="exams/exams_grid.html"), name="exams_grid"),
    path("grid/payments/", TemplateView.as_view(template_name="finance/payments_grid.html"), name="payments_grid"),
    
    # AG Grid API endpoints
    path("api/students/", students_data_api, name="students_api"),
    path("api/classes/", classes_data_api, name="classes_api"),
    path("api/subjects/", subjects_data_api, name="subjects_api"),
    path("api/teachers/", teachers_data_api, name="teachers_api"),
    path("api/attendance/", attendance_data_api, name="attendance_api"),
    path("api/exams/", exams_data_api, name="exams_api"),
    path("api/payments/", payments_data_api, name="payments_api"),
]
