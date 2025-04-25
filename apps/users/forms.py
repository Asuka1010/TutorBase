from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile


class UserUpdateForm(forms.ModelForm):
    """
    A form for updating user information such as username, email, first name, and last name.

    Attributes:
        email (forms.EmailField): Custom email field.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with a Crispy Forms helper for layout customization.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Enable inline help text and remove default form tag
        self.helper.help_text_inline = True
        self.helper.form_tag = False

        # Define layout with Crispy Forms' grid system
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )


class ProfileUpdateForm(forms.ModelForm):
    """
    A form for updating user profile details, including password changes and profile image.

    Attributes:
        password (forms.CharField): Field for entering a new password.
        confirm_password (forms.CharField): Field for confirming the new password.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label="New Password",
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = Profile
        exclude = ('user',)  # Exclude the user field from form input

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with a Crispy Forms helper for layout customization.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # Enable inline help text and remove default form tag
        self.helper.help_text_inline = True
        self.helper.form_tag = False

        # Limit text fields to 2 lines visually
        for field_name in ['subjects_taught', 'languages', 'tools_available']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'rows': 2,
                    'style': 'resize:none; overflow:hidden; height:3.6em;'  # adjust height to approx. 2 lines
                })

        # Define layout with Crispy Forms' grid system
        self.helper.layout = Layout(
            Row(
                Column('password', css_class='form-group col-md-6 mb-0'),
                Column('confirm_password', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'image',  # Include profile image field in the layout,
            'subjects_taught',
            'languages',
            'tools_available',
        )

    def clean(self):
        """
        Validates password fields to ensure they match and meet security requirements.

        Raises:
            forms.ValidationError: If passwords do not match or do not meet validation criteria.

        Returns:
            dict: Cleaned form data.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if password fields are filled and if they match
        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("The two password fields must match.")
            else:
                try:
                    validate_password(password)
                except ValidationError:
                    raise forms.ValidationError(
                        "Password must be at least 8 characters and cannot be too common or similar to your other info."
                    )

        return cleaned_data

    def save(self, commit=True):
        """
        Saves the profile form, updating the password if a new one is provided.

        Args:
            commit (bool): Whether to commit the changes to the database.

        Returns:
            Profile: The updated profile instance.
        """
        instance = super().save(commit=False)  # Get the instance without saving yet

        # Update password only if both fields are filled and match
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password == confirm_password:
            instance.user.set_password(password)
            instance.user.save()  # Save user with new password

        if commit:  # Save the profile instance if commit is True
            instance.save()

        return instance
