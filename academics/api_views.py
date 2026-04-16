from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from academics.models import StudentProfile, SchoolClass, Subject, TeacherProfile
from attendance.models import Attendance
from exams.models import Exam, ExamResult
from finance.models import FeeInvoice, FeePayment

@require_http_methods(["GET"])
def students_data_api(request):
    """Return students data as JSON for AG Grid"""
    students = StudentProfile.objects.select_related('user', 'classroom').values(
        'id', 'user__username', 'user__first_name', 'user__last_name', 
        'user__email', 'classroom__name', 'roll_number', 'user__date_joined'
    )
    
    data = [
        {
            'id': s['id'],
            'name': f"{s['user__first_name']} {s['user__last_name']}".strip(),
            'username': s['user__username'],
            'email': s['user__email'],
            'class': s['classroom__name'],
            'roll': s['roll_number'],
            'joinedDate': s['user__date_joined'].strftime('%Y-%m-%d')
        }
        for s in students
    ]
    return JsonResponse({'data': data})

@require_http_methods(["GET"])
def teachers_data_api(request):
    """Return teachers data as JSON for AG Grid"""
    teachers = TeacherProfile.objects.select_related('user').values(
        'id', 'user__username', 'user__first_name', 'user__last_name',
        'user__email', 'qualification', 'subject_expertise', 'experience_years'
    )
    
    data = [
        {
            'id': t['id'],
            'name': f"{t['user__first_name']} {t['user__last_name']}".strip(),
            'username': t['user__username'],
            'email': t['user__email'],
            'qualification': t['qualification'],
            'expertise': t['subject_expertise'],
            'experience': t['experience_years']
        }
        for t in teachers
    ]
    return JsonResponse({'data': data})

@require_http_methods(["GET"])
def classes_data_api(request):
    """Return classes data as JSON for AG Grid"""
    classes = SchoolClass.objects.values('id', 'name', 'section')
    data = [
        {'id': c['id'], 'name': c['name'], 'section': c['section']}
        for c in classes
    ]
    return JsonResponse({'data': data})

@require_http_methods(["GET"])
def subjects_data_api(request):
    """Return subjects data as JSON for AG Grid"""
    subjects = Subject.objects.values('id', 'name', 'code')
    data = [
        {'id': s['id'], 'name': s['name'], 'code': s['code']}
        for s in subjects
    ]
    return JsonResponse({'data': data})

@require_http_methods(["GET"])
def attendance_data_api(request):
    """Return attendance data as JSON for AG Grid"""
    records = Attendance.objects.select_related('student__user', 'student__classroom').values(
        'id', 'student__user__first_name', 'student__user__last_name', 
        'student__classroom__name', 'date', 'status'
    ).order_by('-date')[:500]
    
    data = [
        {
            'id': r['id'],
            'student': f"{r['student__user__first_name']} {r['student__user__last_name']}".strip(),
            'class': r['student__classroom__name'],
            'date': r['date'].strftime('%Y-%m-%d'),
            'status': r['status']
        }
        for r in records
    ]
    return JsonResponse({'data': data})

@require_http_methods(["GET"])
def exams_data_api(request):
    """Return exams data as JSON for AG Grid"""
    exams = Exam.objects.values('id', 'name', 'subject__name', 'date', 'total_marks')
    data = [
        {
            'id': e['id'],
            'name': e['name'],
            'subject': e['subject__name'],
            'date': e['date'].strftime('%Y-%m-%d'),
            'totalMarks': e['total_marks']
        }
        for e in exams
    ]
    return JsonResponse({'data': data})

@require_http_methods(["GET"])
def payments_data_api(request):
    """Return payments data as JSON for AG Grid"""
    payments = FeePayment.objects.select_related('invoice__student__user').values(
        'id', 'invoice__student__user__first_name', 
        'invoice__student__user__last_name', 'amount', 'payment_date', 'method'
    ).order_by('-payment_date')
    
    data = [
        {
            'id': p['id'],
            'student': f"{p['invoice__student__user__first_name']} {p['invoice__student__user__last_name']}".strip(),
            'amount': str(p['amount']),
            'date': p['payment_date'].strftime('%Y-%m-%d'),
            'method': p['method']
        }
        for p in payments
    ]
    return JsonResponse({'data': data})
