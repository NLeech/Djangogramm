from django.contrib.auth import forms as auth_forms
from django import forms

from .models import User


class LoginForm(auth_forms.AuthenticationForm):
    username = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )


class SignUpForm(auth_forms.UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "username"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.PasswordInput(attrs={'class': 'form-control', })
        self.fields["password2"].widget = forms.PasswordInput(attrs={'class': 'form-control', })


class CompleteRegistrationForm(forms.Form):
    email = forms.EmailField(label="Resend to", widget=forms.EmailInput(attrs={"class": "form-control"}))


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "username", "full_name", "bio", "avatar"]

        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"})
        }
