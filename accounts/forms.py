"""Forms for the accounts app.

Django already ships a UserCreationForm. We are not replacing it, we are just
adding an email field to it.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """The sign-up form: username, first name, email, password, confirm password."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "email")

    def save(self, commit=True):
        # UserCreationForm already knows how to hash and save the password.
        # We just copy our extra fields across.
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")

        if commit:
            user.save()

        return user