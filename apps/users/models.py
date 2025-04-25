from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    """
    Represents a user profile, including a profile image.

    Attributes:
        user (User): A one-to-one relationship with the Django User model.
        image (ImageField): A profile picture with a default image.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics/%Y/%m/%d')
    subjects_taught = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    tools_available = models.TextField(help_text="Zoom, Google Meet, etc", null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the profile.

        Returns:
            str: The username followed by "Profile".
        """
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        """
        Saves the profile instance and resizes the profile image if it's too large.

        - If the image width is greater than 250 pixels, it resizes it proportionally.
        - Helps optimize storage and loading performance.

        Args:
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(Profile, self).save(*args, **kwargs)

        # Open the saved image file
        img = Image.open(self.image.path)

        # Resize the image if the width exceeds 250 pixels
        if img.width > 250:
            output_height = img.height * 250 / img.width  # Maintain aspect ratio
            output_size = (250, int(output_height))  # Convert height to an integer
            img.thumbnail(output_size)  # Resize image
            img.save(self.image.path)  # Save the resized image
