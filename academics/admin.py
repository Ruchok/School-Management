from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import CustomUser
from .models import SchoolClass, StudentProfile, Subject, TeacherProfile


class TeacherProfileAdminForm(forms.ModelForm):
	"""Custom form to allow creating/editing teacher with user details"""
	username = forms.CharField(max_length=150, required=False, help_text="Username for login")
	first_name = forms.CharField(max_length=150, required=False)
	last_name = forms.CharField(max_length=150, required=False)
	email = forms.EmailField(required=False)
	phone = forms.CharField(max_length=20, required=False)
	password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep existing password")
	
	class Meta:
		model = TeacherProfile
		fields = ('qualification', 'specialization', 'joined_on')
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance and self.instance.user:
			self.fields['username'].initial = self.instance.user.username
			self.fields['first_name'].initial = self.instance.user.first_name
			self.fields['last_name'].initial = self.instance.user.last_name
			self.fields['email'].initial = self.instance.user.email
			self.fields['phone'].initial = self.instance.user.phone
			self.fields['password'].required = False
			self.fields['username'].widget.attrs['readonly'] = True
	
	def save(self, commit=True):
		instance = super().save(commit=False)
		
		# Get or create user
		username = self.cleaned_data.get('username')
		if username:
			user, created = CustomUser.objects.get_or_create(
				username=username,
				defaults={
					'first_name': self.cleaned_data.get('first_name', ''),
					'last_name': self.cleaned_data.get('last_name', ''),
					'email': self.cleaned_data.get('email', ''),
					'phone': self.cleaned_data.get('phone', ''),
					'role': 'TEACHER'
				}
			)
			
			# Update user if not newly created
			if not created:
				user.first_name = self.cleaned_data.get('first_name', '')
				user.last_name = self.cleaned_data.get('last_name', '')
				user.email = self.cleaned_data.get('email', '')
				user.phone = self.cleaned_data.get('phone', '')
				
			if self.cleaned_data.get('password'):
				user.set_password(self.cleaned_data.get('password'))
			
			user.save()
			instance.user = user
		
		if commit:
			instance.save()
		return instance


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
	list_display = ("name", "section", "class_teacher")
	search_fields = ("name", "section")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
	form = TeacherProfileAdminForm
	list_display = ("get_teacher_name", "get_email", "get_phone", "qualification", "specialization", "joined_on")
	search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
	
	fieldsets = (
		("Login Credentials", {
			"fields": ("username", "password"),
			"classes": ("collapse",),
			"description": "Only required when creating new teacher. Changes affect teacher login."
		}),
		("Personal Information", {
			"fields": ("first_name", "last_name", "email", "phone")
		}),
		("Professional Details", {
			"fields": ("qualification", "specialization", "joined_on")
		}),
	)
	
	def get_teacher_name(self, obj):
		return obj.user.get_full_name() or obj.user.username
	get_teacher_name.short_description = "Teacher Name"
	
	def get_email(self, obj):
		return obj.user.email
	get_email.short_description = "Email"
	
	def get_phone(self, obj):
		return obj.user.phone
	get_phone.short_description = "Phone"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ("name", "code", "classroom", "teacher")
	list_filter = ("classroom",)
	search_fields = ("name", "code")
	fieldsets = (
		("Basic Information", {
			"fields": ("name", "code")
		}),
		("Assignment", {
			"fields": ("classroom", "teacher")
		}),
	)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("roll_number", "user", "classroom", "admission_date")
	list_filter = ("classroom",)
	search_fields = ("roll_number", "user__username", "user__first_name", "user__last_name")

# Register your models here.
