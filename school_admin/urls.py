from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'school_admin'

urlpatterns = [
    # Authentication
    path('', RedirectView.as_view(url='login/', permanent=False), name='index'),
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Student Management
    path('students/', views.AdminStudentsListView.as_view(), name='students_list'),
    path('students/create/', views.AdminStudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/edit/', views.AdminStudentEditView.as_view(), name='student_edit'),
    path('students/delete/', views.AdminStudentDeleteView.as_view(), name='student_delete'),
    
    # Teacher Management
    path('teachers/', views.AdminTeachersListView.as_view(), name='teachers_list'),
    path('teachers/create/', views.AdminTeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.AdminTeacherEditView.as_view(), name='teacher_edit'),
    path('teachers/delete/', views.AdminTeacherDeleteView.as_view(), name='teacher_delete'),
    
    # Payment Management
    path('payments/', views.AdminPaymentsListView.as_view(), name='payments_list'),
    path('payments/create/', views.AdminPaymentCreateView.as_view(), name='payment_create'),
    
    # Routine Management
    path('routines/', views.AdminRoutinesListView.as_view(), name='routines_list'),
    path('routines/create/', views.AdminRoutineCreateView.as_view(), name='routine_create'),
    path('routines/<int:pk>/edit/', views.AdminRoutineEditView.as_view(), name='routine_edit'),
    path('routines/delete/', views.AdminRoutineDeleteView.as_view(), name='routine_delete'),
    
    # User Management
    path('users/', views.AdminUsersView.as_view(), name='users'),
]
