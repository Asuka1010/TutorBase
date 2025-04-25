from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegistrationViewTest(TestCase):

    def test_registration_page_displays(self):
        """Check the registration form page loads (HTTP 200)."""
        response = self.client.get(reverse('django_registration_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_registration/registration_form.html')

    def test_registration_creates_user(self):
        """Posting valid data to registration form should create a new user."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        }
        response = self.client.post(
            reverse('django_registration_register'),
            data=form_data,
            follow=True
        )
        # Check that the user now exists
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(response.status_code, 200)

    def test_registration_password_mismatch(self):
        """If passwords do not match, the form is invalid, and user is not created."""
        form_data = {
            'username': 'anotheruser',
            'email': 'another@example.com',
            'password1': 'password123',
            'password2': 'mismatch456'
        }
        response = self.client.post(
            reverse('django_registration_register'),
            data=form_data
        )
        self.assertEqual(response.status_code, 200)  # Re-renders the form
        self.assertFalse(User.objects.filter(username='anotheruser').exists())
        form = response.context['form']
        self.assertFormError(form, 'password2', "The two password fields didn’t match.")

    def test_registration_existing_username(self):
        """If the username already exists, it should display an error."""
        User.objects.create_user(username='existinguser', password='existingpass')
        form_data = {
            'username': 'existinguser',
            'email': 'someemail@example.com',
            'password1': 'password123',
            'password2': 'password123'
        }
        response = self.client.post(reverse('django_registration_register'), data=form_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(form, 'username', 'A user with that username already exists.')
