import re

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
        fields = ['classroom', 'admission_date', 'guardian_name', 'guardian_phone']
        labels = {
            'classroom': 'Class',
            'admission_date': 'Admission Date',
            'guardian_name': 'Guardian Name',
            'guardian_phone': 'Guardian Phone',
        }
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r"^[A-Za-z\s]+$", first_name):
            raise forms.ValidationError("First name should only contain letters and spaces.")
        return first_name
        
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r"^[A-Za-z\s]+$", last_name):
            raise forms.ValidationError("Last name should only contain letters and spaces.")
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance.pk and self.instance.user and self.instance.user.username == username:
            return username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        classroom = cleaned_data.get('classroom')
        
        # If it's a new student creation (no primary key), set up the roll number logic
        if not self.instance.pk and classroom:
            count = StudentProfile.objects.filter(classroom=classroom).count()
            parts = classroom.name.split()
            cl_prefix = parts[-1] if parts else "C"
            roll_number = f"{cl_prefix}{classroom.section}-{count + 1:03d}"
            
            # Note: We don't need validation checks for this auto-generated roll number 
            # because we are calculating the next available number logically.
            # We set it directly onto the instance before saving.
            self.instance.roll_number = roll_number
        
        return cleaned_data
    
    def save(self, commit=True):
        student = super().save(commit=False)
        
        if student.user_id:
            user = student.user
        else:
            user = User(username=self.cleaned_data['username'], role='STUDENT')
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not student.user_id:
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
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r"^[A-Za-z\s]+$", first_name):
            raise forms.ValidationError("First name should only contain letters and spaces.")
        return first_name
        
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r"^[A-Za-z\s]+$", last_name):
            raise forms.ValidationError("Last name should only contain letters and spaces.")
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance.pk and self.instance.user and self.instance.user.username == username:
            return username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        if teacher.user_id:
            user = teacher.user
        else:
            user = User(username=self.cleaned_data['username'], role='TEACHER')
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')
        user.phone = self.cleaned_data.get('phone', '')
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not teacher.user_id:
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
