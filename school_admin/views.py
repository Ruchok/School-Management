from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from academics.models import TeacherProfile, StudentProfile, SchoolClass, Subject
from users.models import CustomUser
from finance.models import FeePayment, FeeInvoice
from exams.models import Exam, ExamResult
from .models import ClassRoutine
from .forms import StudentForm, TeacherForm, FeePaymentForm, ClassRoutineForm

_ADMIN_ROLES = {'ADMIN', 'PRINCIPLE_ADMIN', 'ACADEMIC_ADMIN'}


class AdminAuthMixin:
    """Require Django-authenticated school admin / principle admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('school_admin:login')
        is_admin_role = request.user.role in _ADMIN_ROLES
        is_staff = request.user.is_staff or request.user.is_superuser
        if not (is_admin_role or is_staff):
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('school_admin:login')
        return super().dispatch(request, *args, **kwargs)


# ===== AUTHENTICATION VIEWS =====

class AdminLoginView(View):
    """School admin login — authenticates via Django auth, then checks admin role."""

    template_name = 'school_admin/login.html'

    def get(self, request):
        if request.user.is_authenticated and (
            request.user.role in _ADMIN_ROLES
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return redirect('school_admin:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, self.template_name)

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name, {'username': username})

        is_admin_role = user.role in _ADMIN_ROLES
        is_staff = user.is_staff or user.is_superuser

        if not (is_admin_role or is_staff):
            messages.error(
                request,
                'This portal is for School Admin / Principle Admin / Academic Admin only. '
                f'Your account role is "{user.get_role_display()}".'
            )
            return render(request, self.template_name, {'username': username})

        auth_login(request, user)
        # Mark session so templates / legacy checks still work
        request.session['school_admin_authenticated'] = True
        if user.role == 'PRINCIPLE_ADMIN' or user.is_superuser:
            request.session['principle_admin_authenticated'] = True
            request.session['principle_admin'] = True
            messages.success(request, f'Welcome, Principle Admin {user.get_full_name() or user.username}!')
        elif user.role == 'ACADEMIC_ADMIN':
            request.session['principle_admin_authenticated'] = False
            request.session['principle_admin'] = False
            request.session['academic_admin'] = True
            messages.success(request, f'Welcome, Academic Admin {user.get_full_name() or user.username}!')
        else:
            request.session['principle_admin_authenticated'] = False
            request.session['principle_admin'] = False
            messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
        return redirect('school_admin:dashboard')


class AdminLogoutView(View):
    """Logout from admin panel and clear session flags."""

    def get(self, request):
        for key in ('school_admin_authenticated', 'principle_admin_authenticated', 'principle_admin'):
            request.session.pop(key, None)
        auth_logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('home')


# ===== DASHBOARD VIEW =====

class AdminDashboardView(AdminAuthMixin, View):
    """Main admin dashboard"""
    
    template_name = 'school_admin/dashboard.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        context = {
            'is_principle_admin': is_principle_admin,
            'admin_type': 'Principle Admin' if is_principle_admin else 'School Admin',
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
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        return render(request, self.template_name, {
            'students': students.order_by('-admission_date'),
            'classrooms': classrooms,
            'search': search,
            'classroom_filter': classroom_filter,
            'is_principle_admin': is_principle_admin,
        })


class AdminStudentCreateView(AdminAuthMixin, View):
    """Create a new student"""
    
    template_name = 'school_admin/student_form.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = StudentForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add New Student', 'is_principle_admin': is_principle_admin})
    
    def post(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student has been successfully added')
            return redirect('school_admin:students_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add New Student', 'is_principle_admin': is_principle_admin})


class AdminStudentEditView(AdminAuthMixin, View):
    """Edit student details"""
    
    template_name = 'school_admin/student_form.html'
    
    def get(self, request, pk):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        student = get_object_or_404(StudentProfile, pk=pk)
        form = StudentForm(instance=student, initial={
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'username': student.user.username,
            'email': student.user.email,
        })
        return render(request, self.template_name, {'form': form, 'title': f'Edit {student.user.get_full_name()}', 'student': student, 'is_principle_admin': is_principle_admin})
    
    def post(self, request, pk):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        student = get_object_or_404(StudentProfile, pk=pk)
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student has been successfully updated')
            return redirect('school_admin:students_list')
        return render(request, self.template_name, {'form': form, 'title': f'Edit {student.user.get_full_name()}', 'student': student, 'is_principle_admin': is_principle_admin})


class AdminStudentDeleteView(AdminAuthMixin, View):
    """Delete a student - Only Principle Admin can delete"""
    
    def post(self, request):
        # Check if user is Principle Admin
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        if not is_principle_admin:
            messages.error(request, 'Only Principle Admin can delete students.')
            return redirect('school_admin:students_list')
        
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


class AdminStudentSearchView(AdminAuthMixin, View):
    """Search students by name and show their routine"""
    
    template_name = 'school_admin/student_search.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        query = request.GET.get('q', '')
        results = []
        
        if query:
            results = StudentProfile.objects.select_related('user', 'classroom').filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__username__icontains=query) |
                Q(roll_number__icontains=query)
            ).order_by('user__first_name', 'user__last_name')
            
            # Add routine information to each student
            for student in results:
                student.routine = ClassRoutine.objects.filter(
                    classroom=student.classroom
                ).select_related('subject', 'teacher__user').order_by('day_of_week', 'start_time')
        
        return render(request, self.template_name, {
            'query': query,
            'results': results,
            'count': results.count(),
            'is_principle_admin': is_principle_admin
        })


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
        
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        return render(request, self.template_name, {
            'teachers': teachers.order_by('-joined_on'),
            'search': search,
            'is_principle_admin': is_principle_admin,
        })


class AdminTeacherCreateView(AdminAuthMixin, View):
    """Create a new teacher"""
    
    template_name = 'school_admin/teacher_form.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = TeacherForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add New Teacher', 'is_principle_admin': is_principle_admin})
    
    def post(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher has been successfully added')
            return redirect('school_admin:teachers_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add New Teacher', 'is_principle_admin': is_principle_admin})


class AdminTeacherEditView(AdminAuthMixin, View):
    """Edit teacher details"""
    
    template_name = 'school_admin/teacher_form.html'
    
    def get(self, request, pk):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        teacher = get_object_or_404(TeacherProfile, pk=pk)
        form = TeacherForm(instance=teacher, initial={
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'username': teacher.user.username,
            'email': teacher.user.email,
            'phone': getattr(teacher.user, 'phone', ''),
        })
        return render(request, self.template_name, {'form': form, 'title': f'Edit {teacher.user.get_full_name()}', 'teacher': teacher, 'is_principle_admin': is_principle_admin})
    
    def post(self, request, pk):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        teacher = get_object_or_404(TeacherProfile, pk=pk)
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher has been successfully updated')
            return redirect('school_admin:teachers_list')
        return render(request, self.template_name, {'form': form, 'title': f'Edit {teacher.user.get_full_name()}', 'teacher': teacher, 'is_principle_admin': is_principle_admin})


class AdminTeacherDeleteView(AdminAuthMixin, View):
    """Delete a teacher - Only Principle Admin can delete"""
    
    def post(self, request):
        # Check if user is Principle Admin
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        if not is_principle_admin:
            messages.error(request, 'Only Principle Admin can delete teachers.')
            return redirect('school_admin:teachers_list')
        
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
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
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
            'is_principle_admin': is_principle_admin,
        }
        
        return render(request, self.template_name, context)


class AdminPaymentCreateView(AdminAuthMixin, View):
    """Record a new payment"""
    
    template_name = 'school_admin/payment_form.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = FeePaymentForm()
        return render(request, self.template_name, {'form': form, 'title': 'Record New Payment', 'is_principle_admin': is_principle_admin})
    
    def post(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
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
        return render(request, self.template_name, {'form': form, 'title': 'Record New Payment', 'is_principle_admin': is_principle_admin})


# ===== ROUTINE MANAGEMENT VIEWS =====

class AdminRoutinesListView(AdminAuthMixin, View):
    """List all class routines/schedules"""
    
    template_name = 'school_admin/routines_list.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
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
            'is_principle_admin': is_principle_admin,
        })


class AdminRoutineCreateView(AdminAuthMixin, View):
    """Create a new routine entry"""
    
    template_name = 'school_admin/routine_form.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = ClassRoutineForm()
        return render(request, self.template_name, {'form': form, 'title': 'Add New Class Schedule', 'is_principle_admin': is_principle_admin})
    
    def post(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        form = ClassRoutineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class schedule has been successfully added')
            return redirect('school_admin:routines_list')
        return render(request, self.template_name, {'form': form, 'title': 'Add New Class Schedule', 'is_principle_admin': is_principle_admin})


class AdminRoutineEditView(AdminAuthMixin, View):
    """Edit a routine entry"""
    
    template_name = 'school_admin/routine_form.html'
    
    def get(self, request, pk):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        routine = get_object_or_404(ClassRoutine, pk=pk)
        form = ClassRoutineForm(instance=routine)
        return render(request, self.template_name, {'form': form, 'title': f'Edit {routine.classroom} Schedule', 'routine': routine, 'is_principle_admin': is_principle_admin})
    
    def post(self, request, pk):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        routine = get_object_or_404(ClassRoutine, pk=pk)
        form = ClassRoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class schedule has been successfully updated')
            return redirect('school_admin:routines_list')
        return render(request, self.template_name, {'form': form, 'title': f'Edit {routine.classroom} Schedule', 'routine': routine, 'is_principle_admin': is_principle_admin})


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


# ===== RESULT CHECKING VIEW =====

class AdminResultsListView(AdminAuthMixin, View):
    """View and manage exam results"""
    
    template_name = 'school_admin/results_list.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        # Get filter parameters
        search = request.GET.get('search', '')
        exam_filter = request.GET.get('exam', '')
        classroom_filter = request.GET.get('classroom', '')
        
        # Get all results with related data
        results = ExamResult.objects.select_related(
            'exam', 'exam__classroom', 'student', 'student__user', 'student__classroom'
        ).all()
        
        # Apply filters
        if search:
            results = results.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__user__username__icontains=search) |
                Q(exam__title__icontains=search)
            )
        
        if exam_filter:
            results = results.filter(exam__id=exam_filter)
        
        if classroom_filter:
            results = results.filter(exam__classroom__id=classroom_filter)
        
        # Get exams and classrooms for filter dropdowns
        exams = Exam.objects.all().order_by('-exam_date')
        classrooms = SchoolClass.objects.all()
        
        # Add stats
        total_results = ExamResult.objects.count()
        avg_marks = ExamResult.objects.values('exam').annotate(avg=Count('marks'))
        
        context = {
            'results': results.order_by('-exam__exam_date')[:100],  # Paginate in future
            'exams': exams,
            'classrooms': classrooms,
            'total_results': total_results,
            'search': search,
            'exam_filter': exam_filter,
            'classroom_filter': classroom_filter,
            'is_principle_admin': is_principle_admin,
        }
        
        return render(request, self.template_name, context)


class AdminResultDetailView(AdminAuthMixin, View):
    """View detailed results for an exam"""
    
    template_name = 'school_admin/exam_results_detail.html'
    
    def get(self, request, exam_id):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        
        exam = get_object_or_404(Exam, id=exam_id)
        results = ExamResult.objects.filter(exam=exam).select_related(
            'student', 'student__user', 'student__classroom'
        ).order_by('student__user__first_name')
        
        # Calculate statistics
        total_students = results.count()
        avg_marks = sum(r.marks for r in results) / total_students if total_students > 0 else 0
        highest_marks = max((r.marks for r in results), default=0)
        lowest_marks = min((r.marks for r in results), default=0)
        
        grade_distribution = {}
        for result in results:
            grade = result.grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        context = {
            'exam': exam,
            'results': results,
            'total_students': total_students,
            'avg_marks': round(avg_marks, 2),
            'highest_marks': highest_marks,
            'lowest_marks': lowest_marks,
            'grade_distribution': grade_distribution,
            'is_principle_admin': is_principle_admin,
        }
        
        return render(request, self.template_name, context)


# ===== USER MANAGEMENT VIEW =====

class AdminUsersView(AdminAuthMixin, View):
    """Manage all users"""
    
    template_name = 'school_admin/users.html'
    
    def get(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
        users = CustomUser.objects.all().order_by('-date_joined')
        return render(request, self.template_name, {'users': users, 'is_principle_admin': is_principle_admin})
    
    def post(self, request):
        is_principle_admin = request.session.get('principle_admin_authenticated', False)
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
