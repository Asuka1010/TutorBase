from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthViewsTest(TestCase):

    def setUp(self):
        # Create a user for login tests
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username,
            email='test@example.com',
            password=self.password
        )

    def test_login_page_displays(self):
        """Check the login page loads successfully (HTTP 200)."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_valid_credentials(self):
        """Posting valid credentials to login should redirect to next page (or default)."""
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(reverse('login'), data=data, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        # TODO: Add redirect test once home is built out.

    def test_login_invalid_credentials(self):
        """Posting invalid credentials should not authenticate the user."""
        data = {
            'username': self.username,
            'password': 'wrong_password'
        }
        response = self.client.post(reverse('login'), data=data)
        # The response status_code is 200 but user is not authenticated
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """A logged-in user should be able to log out and be redirected to home."""
        self.client.login(username=self.username, password=self.password)

        response = self.client.post(reverse('logout'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

        self.assertIn((reverse('home'), 302), response.redirect_chain)