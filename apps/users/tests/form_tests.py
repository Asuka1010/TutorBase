from django.test import TestCase
from django.contrib.auth.models import User
from apps.users.forms import UserUpdateForm, ProfileUpdateForm
from apps.users.models import Profile
from django.core.exceptions import ValidationError


class UserUpdateFormTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='old_username',
            email='old_email@example.com',
            password='password123'
        )

    def test_form_valid_data(self):
        """Form should be valid with all required fields correctly filled."""
        form_data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated_user = form.save()
        self.assertEqual(updated_user.username, 'new_username')
        self.assertEqual(updated_user.email, 'new_email@example.com')
        self.assertEqual(updated_user.first_name, 'John')
        self.assertEqual(updated_user.last_name, 'Doe')

    def test_form_missing_email(self):
        """If 'email' is required, form should be invalid without it."""
        form_data = {
            'username': 'testuser',
            'email': '',  # empty
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_invalid_email(self):
        """An invalid email address should make the form invalid."""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',  # not a valid format
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class ProfileUpdateFormTest(TestCase):

    def setUp(self):
        # Create a user and a related profile
        self.user = User.objects.create_user(
            username='old_username',
            email='old_email@example.com',
            password='old_password123'
        )
        self.profile = self.user.profile # Profile.objects.create(user=self.user, image='default.jpg')

    def test_no_password_change(self):
        """
        Leaving password fields blank should not change the user's password.
        """
        form_data = {
            'password': '',
            'confirm_password': ''
        }
        form = ProfileUpdateForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated_profile = form.save()
        # Old password remains unchanged
        self.assertTrue(updated_profile.user.check_password('old_password123'))

    def test_passwords_must_match(self):
        """
        If password and confirm_password differ, the form should be invalid.
        """
        form_data = {
            'password': 'newpassword123',
            'confirm_password': 'mismatchpassword',
        }
        form = ProfileUpdateForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        # The error is usually raised as a form-wide (non-field) error
        self.assertIn('__all__', form.errors)
        self.assertIn(
            'The two password fields must match.',
            form.errors['__all__']
        )

    def test_valid_password_change(self):
        """
        Changing a valid password updates the user's password in the database.
        """
        form_data = {
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
        }
        form = ProfileUpdateForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated_profile = form.save()
        self.user.refresh_from_db()
        self.assertTrue(updated_profile.user.check_password('newpassword123'))

    def test_password_too_short_fails_validation(self):
        """
        A short password should fail Django's password validation (assuming you have
        a MinimumLengthValidator in AUTH_PASSWORD_VALIDATORS).
        """
        form_data = {
            'password': '123',
            'confirm_password': '123',
        }
        form = ProfileUpdateForm(data=form_data, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Password must be at least', form.errors['__all__'][0])

    def test_save_with_commit_true(self):
        """With commit=True, the profile should be saved immediately."""
        form = ProfileUpdateForm(data={}, instance=self.profile)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated_profile = form.save(commit=True)
        # Confirm the changes are persisted
        self.assertIsNotNone(updated_profile.pk)
        self.assertTrue(Profile.objects.filter(pk=updated_profile.pk).exists())

    def test_save_with_commit_false(self):
        """
        With commit=False, changes shouldn't be saved until we explicitly save the instance.
        """
        form = ProfileUpdateForm(data={}, instance=self.profile)
        self.assertTrue(form.is_valid(), msg=form.errors)
        updated_profile = form.save(commit=False)
        # The returned instance is not yet saved to the database with new changes
        # But the profile does exist originally, so be careful about how you test "not saved."
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.image, 'default.jpg')

        # Let's pretend we change the image before calling save
        updated_profile.image = 'default.jpg'
        updated_profile.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.image, 'default.jpg')
