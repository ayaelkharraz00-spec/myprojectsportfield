

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation, Terrain, Sport
import datetime


class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 'class': 'form-control',
            'min': datetime.date.today().isoformat(),
        })
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    duration = forms.ChoiceField(
        choices=[(1,'1 hour'),(2,'2 hours'),(3,'3 hours'),(4,'4 hours')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model  = Reservation
        fields = ['date', 'start_time', 'duration']

    def clean_duration(self):
        return int(self.cleaned_data['duration'])


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'})
    )

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TerrainFilterForm(forms.Form):
    search = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '🔍 Search by name…'})
    )
    sport = forms.ModelChoiceField(queryset=Sport.objects.all(), required=False,
        empty_label='All Sports', widget=forms.Select(attrs={'class': 'form-select'})
    )
    availability = forms.ChoiceField(
        choices=[('','All'),('yes','✅ Available'),('no','❌ Unavailable')],
        required=False, widget=forms.Select(attrs={'class': 'form-select'})
    )
