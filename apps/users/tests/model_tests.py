from django.contrib.auth.models import User
from django.test import TestCase
from apps.users.models import Profile

import tempfile
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone


class ProfileModelTest(TestCase):

    def tearDown(self):
        for profile in Profile.objects.all():
            if profile.image and "default.jpg" not in profile.image.name:
                profile.image.delete(save=False)

    def test_profile_creation(self):
        user = User.objects.create(username='testuser')
        profile = user.profile # Profile.objects.create(user=user)
        self.assertEqual(profile.user.username, 'testuser')
        self.assertTrue(profile.image)  # Ensures the default is set if none provided

    def test_profile_str_method(self):
        user = User.objects.create(username='testuser')
        profile = user.profile # Profile.objects.create(user=user)
        self.assertEqual(str(profile), 'testuser Profile')

    def test_profile_default_image(self):
        user = User.objects.create(username='testuser')
        profile = user.profile # Profile.objects.create(user=user)
        self.assertIn('default.jpg', profile.image.name)

    def test_upload_to_directory_structure(self):
        user = User.objects.create(username='testuser')
        # Create an in-memory image
        image = Image.new('RGB', (300, 300), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(temp_file, format='PNG')
        temp_file.seek(0)

        # Create a Django-friendly file
        uploaded_file = SimpleUploadedFile(
            name='test.png',
            content=temp_file.read(),
            content_type='image/png'
        )
        # Create profile with this image
        year = timezone.now().strftime('%Y')
        month = timezone.now().strftime('%m')
        day = timezone.now().strftime('%d')

        self.profile = user.profile # Profile.objects.create(user=user, image=uploaded_file)
        self.profile.image = uploaded_file
        self.profile.save()

        # Register a cleanup function to delete the file at the end of the test
        self.addCleanup(self.profile.image.delete, save=False)

        self.assertIn(f'profile_pics/{year}/{month}/{day}/test.png', self.profile.image.name)

    def test_user_deletion_cascades_to_profile(self):
        user = User.objects.create(username='testuser')
        profile = user.profile # Profile.objects.create(user=user)

        user.delete()
        # Profile should be deleted automatically
        self.assertFalse(Profile.objects.filter(pk=profile.pk).exists())


class ProfileImageResizeTest(TestCase):

    def tearDown(self):
        for profile in Profile.objects.all():
            if profile.image and "default.jpg" not in profile.image.name:
                profile.image.delete(save=False)

    def create_test_image(self, width, height, color='blue'):
        """Helper method to create an in-memory test image."""
        image = Image.new('RGB', (width, height), color=color)
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        return temp_file

    def test_image_resize_if_over_250_width(self):
        # Create an image wider than 250px
        temp_file = self.create_test_image(500, 400)
        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=temp_file.read(),
            content_type='image/jpeg'
        )

        user = User.objects.create(username='testuser')
        profile = user.profile # Profile.objects.create(user=user, image=uploaded_file)
        profile.image = uploaded_file
        profile.save()
        profile.refresh_from_db()  # Ensure we have the latest data from the database

        # Open the saved image from the profile
        img = Image.open(profile.image.path)
        self.assertLessEqual(img.width, 250)  # The width should be at most 250
        # Check the aspect ratio was maintained
        expected_height = int(400 * (250 / 500))  # 400 * 0.5 = 200
        self.assertEqual(img.height, expected_height)

    def test_no_resize_if_width_below_250(self):
        # Create an image that is 200px wide
        temp_file = self.create_test_image(200, 200)
        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=temp_file.read(),
            content_type='image/jpeg'
        )

        user = User.objects.create(username='testuser')
        profile = user.profile # Profile.objects.create(user=user, image=uploaded_file)
        profile.image = uploaded_file
        profile.save()
        profile.refresh_from_db()

        img = Image.open(profile.image.path)
        # Should remain unchanged because it's already below the threshold
        self.assertEqual(img.width, 200)
        self.assertEqual(img.height, 200)