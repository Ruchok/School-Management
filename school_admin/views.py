from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from academics.models import TeacherProfile, StudentProfile, SchoolClass, Subject
from users.models import CustomUser
from finance.models import FeePayment, FeeInvoice
from .models import ClassRoutine
from .forms import StudentForm, TeacherForm, FeePaymentForm, ClassRoutineForm


class AdminAuthMixin:
    """Mixin to check if user is authenticated as school admin"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('school_admin_authenticated', False):
            return redirect('school_admin:login')
        return super().dispatch(request, *args, **kwargs)


# ===== AUTHENTICATION VIEWS =====

class AdminLoginView(View):
    """Custom admin login with password"""
    
    template_name = 'school_admin/login.html'
    
    def get(self, request):
        if request.session.get('school_admin_authenticated', False):
            return redirect('school_admin:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        password = request.POST.get('password', '')
        admin_password = getattr(settings, 'SCHOOL_ADMIN_PASSWORD', 'Admin@123')
        
        if password == admin_password:
            request.session['school_admin_authenticated'] = True
            request.session.set_expiry(3600)  # 1 hour expiry
            messages.success(request, 'You have successfully logged in to the Admin Panel')
            return redirect('school_admin:dashboard')
        else:
            messages.error(request, 'Invalid password. Please try again.')
            return render(request, self.template_name)


class AdminLogoutView(View):
    """Logout from admin panel"""
    
    def get(self, request):
        if 'school_admin_authenticated' in request.session:
            del request.session['school_admin_authenticated']
        messages.success(request, 'You have successfully logged out')
        return redirect('school_admin:login')


# ===== DASHBOARD VIEW =====

class AdminDashboardView(AdminAuthMixin, View):
    """Main admin dashboard"""
    
    template_name = 'school_admin/dashboard.html'
    
    def get(self, request):
        context = {
            'total_teachers': TeacherProfile.objects.count(),
            'total_students': StudentProfile.objects.count(),
            'total_classes': SchoolClass.objects.count(),
            'total_users': CustomUser.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_routines': ClassRoutine.objects.count(),
            
            # Financial stats
            'total_pending': FeeInvoice.objects.filter(status='PENDING').count(),
            'total_partial': FeeInvoice.objects.filter(status='PARTIAL').count(),
            'total_paid': FeeInvoice.objects.filter(status='PAID').count(),
            
            # Recent data
            'recent_teachers': TeacherProfile.objects.select_related('user').order_by('-joined_on')[:5],
            'recent_students': StudentProfile.objects.select_related('user').order_by('-admission_date')[:5],
            'recent_payments': FeePayment.objects.select_related('invoice', 'invoice__student__user').order_by('-payment_date')[:5],
            
            # Statistics by role
            'users_by_role': CustomUser.objects.values('role').annotate(count=Count('id')),
        }
        
        return render(request, self.template_name, context)


# ===== STUDENT MANAGEMENT VIEWS =====

class AdminStudentsListView(AdminAuthMixin, View):
    """List all students"""
    
    template_name = 'school_admin/students_list.html'
    
    def get(self, request):
        search = request.GET.get('search', '')
        classroom_filter = request.GET.get('classroom', '')
        
        students = StudentProfile.objects.select_related('user', 'classroom').all()
        
        if search:
            students = students.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(roll_number__icontains=search)
            )
        
        if classroom_filter:
            students = students.filter(classroom_id=classroom_filter)
        
        classrooms = SchoolClass.objects.all()
        
        return render(request, self.template_name, {
            'students': students.order_by('-admission_date'),
            'classrooms': classrooms,
            'search': search,
            'classroom_filter': classroom_filter,
        })


class AdminStudentCreateView(AdminAuthMixin, View):
    """Create a new student"""
    
    template_name = 'school_admin/student_form.html'
    
    def get(self, request):
        form = StudentForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add New Student'})
    
    def post(self, request):
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student has been successfully added')
            return redirect('school_admin:students_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add New Student'})


class AdminStudentEditView(AdminAuthMixin, View):
    """Edit student details"""
    
    template_name = 'school_admin/student_form.html'
    
    def get(self, request, pk):
        student = get_object_or_404(StudentProfile, pk=pk)
        form = StudentForm(instance=student, initial={
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'username': student.user.username,
            'email': student.user.email,
        })
        return render(request, self.template_name, {'form': form, 'title': f'Edit {student.user.get_full_name()}', 'student': student})
    
    def post(self, request, pk):
        student = get_object_or_404(StudentProfile, pk=pk)
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student has been successfully updated')
            return redirect('school_admin:students_list')
        return render(request, self.template_name, {'form': form, 'title': f'Edit {student.user.get_full_name()}', 'student': student})


class AdminStudentDeleteView(AdminAuthMixin, View):
    """Delete a student"""
    
    def post(self, request):
        student_id = request.POST.get('student_id')
        try:
            student = StudentProfile.objects.get(id=student_id)
            user = student.user
            name = user.get_full_name()
            student.delete()
            user.delete()
            messages.success(request, f'Student "{name}" has been successfully deleted')
        except StudentProfile.DoesNotExist:
            messages.error(request, 'Student not found')
        
        return redirect('school_admin:students_list')


# ===== TEACHER MANAGEMENT VIEWS =====

class AdminTeachersListView(AdminAuthMixin, View):
    """List all teachers"""
    
    template_name = 'school_admin/teachers_list.html'
    
    def get(self, request):
        search = request.GET.get('search', '')
        
        teachers = TeacherProfile.objects.select_related('user').all()
        
        if search:
            teachers = teachers.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(qualification__icontains=search) |
                Q(specialization__icontains=search)
            )
        
        return render(request, self.template_name, {
            'teachers': teachers.order_by('-joined_on'),
            'search': search,
        })


class AdminTeacherCreateView(AdminAuthMixin, View):
    """Create a new teacher"""
    
    template_name = 'school_admin/teacher_form.html'
    
    def get(self, request):
        form = TeacherForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add New Teacher'})
    
    def post(self, request):
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher has been successfully added')
            return redirect('school_admin:teachers_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add New Teacher'})


class AdminTeacherEditView(AdminAuthMixin, View):
    """Edit teacher details"""
    
    template_name = 'school_admin/teacher_form.html'
    
    def get(self, request, pk):
        teacher = get_object_or_404(TeacherProfile, pk=pk)
        form = TeacherForm(instance=teacher, initial={
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'username': teacher.user.username,
            'email': teacher.user.email,
            'phone': getattr(teacher.user, 'phone', ''),
        })
        return render(request, self.template_name, {'form': form, 'title': f'Edit {teacher.user.get_full_name()}', 'teacher': teacher})
    
    def post(self, request, pk):
        teacher = get_object_or_404(TeacherProfile, pk=pk)
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher has been successfully updated')
            return redirect('school_admin:teachers_list')
        return render(request, self.template_name, {'form': form, 'title': f'Edit {teacher.user.get_full_name()}', 'teacher': teacher})


class AdminTeacherDeleteView(AdminAuthMixin, View):
    """Delete a teacher"""
    
    def post(self, request):
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = TeacherProfile.objects.get(id=teacher_id)
            user = teacher.user
            name = user.get_full_name()
            teacher.delete()
            user.delete()
            messages.success(request, f'Teacher "{name}" has been successfully deleted')
        except TeacherProfile.DoesNotExist:
            messages.error(request, 'Teacher not found')
        
        return redirect('school_admin:teachers_list')


# ===== PAYMENT MANAGEMENT VIEWS =====

class AdminPaymentsListView(AdminAuthMixin, View):
    """List all fee payments"""
    
    template_name = 'school_admin/payments_list.html'
    
    def get(self, request):
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        payments = FeePayment.objects.select_related('invoice', 'invoice__student__user', 'received_by').all()
        invoices = FeeInvoice.objects.select_related('student__user', 'fee_structure').all()
        
        if search:
            invoices = invoices.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__roll_number__icontains=search)
            )
        
        if status_filter:
            invoices = invoices.filter(status=status_filter)
        
        context = {
            'payments': payments.order_by('-payment_date'),
            'invoices': invoices.order_by('-issued_on'),
            'search': search,
            'status_filter': status_filter,
            'statuses': ['PENDING', 'PARTIAL', 'PAID'],
        }
        
        return render(request, self.template_name, context)


class AdminPaymentCreateView(AdminAuthMixin, View):
    """Record a new payment"""
    
    template_name = 'school_admin/payment_form.html'
    
    def get(self, request):
        form = FeePaymentForm()
        return render(request, self.template_name, {'form': form, 'title': 'Record New Payment'})
    
    def post(self, request):
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user if not request.user.is_anonymous else None
            payment.save()
            
            # Update invoice status
            invoice = payment.invoice
            invoice.amount_paid += payment.amount
            invoice.save()
            
            messages.success(request, f'Payment of {payment.amount} has been recorded successfully')
            return redirect('school_admin:payments_list')
        return render(request, self.template_name, {'form': form, 'title': 'Record New Payment'})


# ===== ROUTINE MANAGEMENT VIEWS =====

class AdminRoutinesListView(AdminAuthMixin, View):
    """List all class routines/schedules"""
    
    template_name = 'school_admin/routines_list.html'
    
    def get(self, request):
        classroom_filter = request.GET.get('classroom', '')
        day_filter = request.GET.get('day', '')
        
        routines = ClassRoutine.objects.select_related('classroom', 'subject', 'teacher__user').all()
        
        if classroom_filter:
            routines = routines.filter(classroom_id=classroom_filter)
        
        if day_filter:
            routines = routines.filter(day_of_week=day_filter)
        
        classrooms = SchoolClass.objects.all()
        days = [
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
        ]
        
        return render(request, self.template_name, {
            'routines': routines.order_by('classroom', 'day_of_week', 'start_time'),
            'classrooms': classrooms,
            'days': days,
            'classroom_filter': classroom_filter,
            'day_filter': day_filter,
        })


class AdminRoutineCreateView(AdminAuthMixin, View):
    """Create a new routine entry"""
    
    template_name = 'school_admin/routine_form.html'
    
    def get(self, request):
        form = ClassRoutineForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add New Class Schedule'})
    
    def post(self, request):
        form = ClassRoutineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class schedule has been successfully added')
            return redirect('school_admin:routines_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add New Class Schedule'})


class AdminRoutineEditView(AdminAuthMixin, View):
    """Edit a routine entry"""
    
    template_name = 'school_admin/routine_form.html'
    
    def get(self, request, pk):
        routine = get_object_or_404(ClassRoutine, pk=pk)
        form = ClassRoutineForm(instance=routine)
        return render(request, self.template_name, {'form': form, 'title': f'Edit {routine.classroom} Schedule', 'routine': routine})
    
    def post(self, request, pk):
        routine = get_object_or_404(ClassRoutine, pk=pk)
        form = ClassRoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class schedule has been successfully updated')
            return redirect('school_admin:routines_list')
        return render(request, self.template_name, {'form': form, 'title': f'Edit {routine.classroom} Schedule', 'routine': routine})


class AdminRoutineDeleteView(AdminAuthMixin, View):
    """Delete a routine entry"""
    
    def post(self, request):
        routine_id = request.POST.get('routine_id')
        try:
            routine = ClassRoutine.objects.get(id=routine_id)
            classroom = routine.classroom
            day = routine.day_of_week
            routine.delete()
            messages.success(request, f'Schedule for {classroom} on {day} has been deleted')
        except ClassRoutine.DoesNotExist:
            messages.error(request, 'Schedule not found')
        
        return redirect('school_admin:routines_list')


# ===== USER MANAGEMENT VIEW =====

class AdminUsersView(AdminAuthMixin, View):
    """Manage all users"""
    
    template_name = 'school_admin/users.html'
    
    def get(self, request):
        users = CustomUser.objects.all().order_by('-date_joined')
        return render(request, self.template_name, {'users': users})
    
    def post(self, request):
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action == 'delete':
            try:
                user = CustomUser.objects.get(id=user_id)
                username = user.username
                user.delete()
                messages.success(request, f'User "{username}" has been successfully deleted')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found')
        
        return redirect('school_admin:users')
