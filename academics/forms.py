from django import forms

from users.models import CustomUser

from .models import SchoolClass, StudentProfile, Subject


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "section", "class_teacher"]


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code", "classroom", "teacher"]


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
