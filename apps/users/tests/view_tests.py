from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.users.models import Profile
from django.contrib import messages


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user with an email
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='testuser@example.com',
            first_name='test',
            last_name='user'
        )
        self.url = reverse('profile')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        # Check that it redirects to login page
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_successful_get_if_logged_in(self):
        """
        Verifies that a logged-in user can view the profile page
        and sees their username, email, and profile image.
        """
        # Log in the user
        self.client.login(username='testuser', password='testpass')

        # Create a profile with a fake image path (or a default image).
        profile = self.user.profile

        # Make the GET request
        response = self.client.get(self.url)

        # Basic checks
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

        # Ensure username and email appear in the page content
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'testuser@example.com')
        self.assertContains(response, profile.image.url)


class UserProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='old_email@example.com',
            password='testpass'
        )
        # Create a Profile linked to this user
        self.profile = self.user.profile
        self.url = reverse('profile_edit')  # The URL pattern for UserProfileUpdateView

    def test_redirect_if_not_logged_in(self):
        # Attempt to GET while logged out
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_get_request_if_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')
        # Ensure the forms are in the context
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)

    def test_valid_post_updates_user_and_profile(self):
        self.client.login(username='testuser', password='testpass')

        # POST data for user form and profile form
        post_data = {
            'username': 'updateduser',  # from UserUpdateForm
            'email': 'new_email@example.com',  # from UserUpdateForm
        }

        response = self.client.post(self.url, post_data, follow=True)

        # After a successful update, it should redirect to the 'profile' page
        self.assertRedirects(response, reverse('profile'))

        # Refresh from database to check updates
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        # Check that the data was updated
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'new_email@example.com')

        # Check success message
        message_list = list(response.context['messages'])
        self.assertTrue(any('Your account has been updated!' in str(msg) for msg in message_list))

    def test_invalid_post_does_not_save(self):
        self.client.login(username='testuser', password='testpass')

        # Provide invalid data for the user form, e.g. empty username if that's invalid
        post_data = {
            'username': '',  # Invalid if blank is not allowed
            'email': 'not-an-email',  # Potentially invalid if your form checks format
        }

        response = self.client.post(self.url, post_data)

        # Should re-render the same template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')

        # Confirm the user or profile wasn't updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')  # Still the old value
        self.assertEqual(self.user.email, 'old_email@example.com')  # Still the old value