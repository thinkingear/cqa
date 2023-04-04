from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms import ModelForm, Form


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        for field in self.fields:
            if field in cleaned_data:
                cleaned_data[field] = cleaned_data[field].strip()

        return cleaned_data


class LoginForm(Form):
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")


