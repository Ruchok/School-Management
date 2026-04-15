from django import forms
from django.contrib.auth import get_user_model
from academics.models import TeacherProfile, StudentProfile, SchoolClass
from finance.models import FeePayment, FeeInvoice
from .models import ClassRoutine

User = get_user_model()


class StudentForm(forms.ModelForm):
    """Form for creating and editing student profiles"""
    
    first_name = forms.CharField(max_length=50, required=True, label='First Name')
    last_name = forms.CharField(max_length=50, required=True, label='Last Name')
    username = forms.CharField(max_length=150, required=True, label='Username')
    email = forms.EmailField(required=False, label='Email')
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Password (leave blank to keep current)')
    
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'classroom', 'admission_date', 'guardian_name', 'guardian_phone']
        labels = {
            'roll_number': 'Roll Number',
            'classroom': 'Class',
            'admission_date': 'Admission Date',
            'guardian_name': 'Guardian Name',
            'guardian_phone': 'Guardian Phone',
        }
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow the same username if editing an existing student
        if self.instance.pk and self.instance.user and self.instance.user.username == username:
            return username
        # Check if username already exists for new students
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
        # Get or create user
        if student.user_id:
            user = student.user
        else:
            user = User(username=self.cleaned_data['username'], role='STUDENT')
        
        # Update user fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')
        
        # Set password - generate default if not provided during creation
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not student.user_id:  # Only set default password for new users
            # Set a default password using username
            default_password = f"Student@{self.cleaned_data['username']}"
            user.set_password(default_password)
        
        user.save()
        student.user = user
        
        if commit:
            student.save()
        return student


class TeacherForm(forms.ModelForm):
    """Form for creating and editing teacher profiles"""
    
    first_name = forms.CharField(max_length=50, required=True, label='First Name')
    last_name = forms.CharField(max_length=50, required=True, label='Last Name')
    username = forms.CharField(max_length=150, required=True, label='Username')
    email = forms.EmailField(required=False, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Phone')
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Password (leave blank to keep current)')
    
    class Meta:
        model = TeacherProfile
        fields = ['qualification', 'specialization', 'joined_on']
        labels = {
            'qualification': 'Qualification',
            'specialization': 'Specialization',
            'joined_on': 'Joined Date',
        }
        widgets = {
            'joined_on': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Allow the same username if editing an existing teacher
        if self.instance.pk and self.instance.user and self.instance.user.username == username:
            return username
        # Check if username already exists for new teachers
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        # Get or create user
        if teacher.user_id:
            user = teacher.user
        else:
            user = User(username=self.cleaned_data['username'], role='TEACHER')
        
        # Update user fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')
        user.phone = self.cleaned_data.get('phone', '')
        
        # Set password - generate default if not provided during creation
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not teacher.user_id:  # Only set default password for new users
            # Set a default password using username
            default_password = f"Teacher@{self.cleaned_data['username']}"
            user.set_password(default_password)
        
        user.save()
        teacher.user = user
        
        if commit:
            teacher.save()
        return teacher


class FeePaymentForm(forms.ModelForm):
    """Form for recording fee payments"""
    
    class Meta:
        model = FeePayment
        fields = ['invoice', 'amount', 'method']
        labels = {
            'invoice': 'Invoice',
            'amount': 'Amount Paid',
            'method': 'Payment Method',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }


class ClassRoutineForm(forms.ModelForm):
    """Form for managing class routines/schedules"""
    
    class Meta:
        model = ClassRoutine
        fields = ['classroom', 'subject', 'day_of_week', 'start_time', 'end_time', 'teacher', 'room_number']
        labels = {
            'classroom': 'Class',
            'subject': 'Subject',
            'day_of_week': 'Day',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'teacher': 'Teacher',
            'room_number': 'Room Number',
        }
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
