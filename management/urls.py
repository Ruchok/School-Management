"""URL configuration for management project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core.views import (
    DashboardView,
    HomePageView,
    StudentLoginView,
    TeacherLoginView,
    AccountantLoginView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Role-separated login portals
    path('login/student/', StudentLoginView.as_view(), name='login_student'),
    path('login/teacher/', TeacherLoginView.as_view(), name='login_teacher'),
    path('login/accountant/', AccountantLoginView.as_view(), name='login_accountant'),
    # Admin / Principle Admin / Superuser → /school-admin/login/

    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('school-admin/', include('school_admin.urls')),
    path('academics/', include('academics.urls')),
    path('attendance/', include('attendance.urls')),
    path('exams/', include('exams.urls')),
    path('finance/', include('finance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
