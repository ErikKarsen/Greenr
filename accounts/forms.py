from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from django.forms import ModelForm
from .models import Journey, Customer


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class JourneyForm(ModelForm):
    class Meta:
        model = Journey
        fields = ['transportation', 'duration_hours', 'duration_minutes']


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user', 'username', 'email']
        widgets = {
            'profile_pic': forms.FileInput,
        } 