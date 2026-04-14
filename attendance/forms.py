from django import forms

from academics.models import SchoolClass

from .models import Attendance


class AttendanceDayForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["classroom", "date", "notes"]


class AttendanceBulkForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=SchoolClass.objects.all())
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
