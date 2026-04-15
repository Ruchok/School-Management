from django import forms

from users.models import CustomUser

from .models import SchoolClass, StudentProfile, Subject, TeacherProfile


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "section", "class_teacher"]


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code", "classroom", "teacher"]


class TeacherCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")
    first_name = forms.CharField(max_length=150, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    email = forms.EmailField(required=False, label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")

    class Meta:
        model = TeacherProfile
        fields = [
            "qualification",
            "specialization",
            "joined_on",
        ]

    def clean_username(self):
        """Validate that username is unique"""
        username = self.cleaned_data.get("username")
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username already exists. Please choose a different one.")
        return username

    def clean_email(self):
        """Validate email if provided"""
        email = self.cleaned_data.get("email")
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        """Additional form validation"""
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        
        if not username:
            raise forms.ValidationError("Username is required.")
        if not password:
            raise forms.ValidationError("Password is required.")
        
        return cleaned_data

    def save(self, commit=True):
        try:
            user = CustomUser.objects.create_user(
                username=self.cleaned_data["username"],
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                email=self.cleaned_data["email"],
                phone=self.cleaned_data.get("phone", ""),
                role=CustomUser.Roles.TEACHER,
                password=self.cleaned_data["password"],
            )

            profile = super().save(commit=False)
            profile.user = user
            if commit:
                profile.save()
            return profile
        except Exception as e:
            raise forms.ValidationError(f"Error creating teacher: {str(e)}")


class StudentCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = StudentProfile
        fields = [
            "roll_number",
            "classroom",
            "admission_date",
            "guardian_name",
            "guardian_phone",
        ]

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
            role=CustomUser.Roles.STUDENT,
            password=self.cleaned_data["password"],
        )

        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return profile
