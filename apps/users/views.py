from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Displays the user profile page.

    Attributes:
        template_name (str): The HTML template used to render the profile page.
    """
    template_name = 'users/profile.html'


class UserProfileUpdateView(LoginRequiredMixin, View):
    """
    Handles updating the user profile.

    This view allows users to edit their personal details (username, email, etc.)
    and profile information (profile picture, password, etc.).

    Attributes:
        template_name (str): The HTML template used for the profile update page.
    """
    template_name = 'users/profile_edit.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to display the user update form.

        Args:
            request (HttpRequest): The request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The rendered profile update form.
        """
        user_form = UserUpdateForm(instance=request.user)  # Pre-fill form with user data
        profile_form = ProfileUpdateForm(instance=request.user.profile)  # Pre-fill profile data
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update the user profile.

        Validates and saves the updated user and profile information.
        If successful, displays a success message and redirects to the profile page.

        Args:
            request (HttpRequest): The request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to the profile page on success.
            HttpResponse: Renders the profile edit page with validation errors on failure.
        """
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()  # Save user data
            profile_form.save()  # Save profile data
            messages.success(request, 'Your account has been updated!')  # Display success message
            return redirect('profile')  # Redirect to the profile page

        # Re-render the form with errors if validation fails
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })
