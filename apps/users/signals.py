from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Signal handler that creates or updates a user's profile when a User instance is saved.

    If the profile already exists, it attempts to save it. If it does not exist,
    a new Profile instance is created.

    Additionally, when a new profile is created:
    - Assigns the first available Letter as a `LetterCard` to the user.
    - Assigns the first available Content as a `ContentCard` to the user.

    Args:
        sender (Model): The model class that triggered the signal (`User` in this case).
        instance (User): The instance of the User model that was saved.
        created (bool): Boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """

    try:
        # Attempt to save the existing profile if it exists
        instance.profile.save()
    except Profile.DoesNotExist:
        # print("Creating profile")
        # If the profile does not exist, create a new one
        Profile.objects.get_or_create(user=instance)

        # Extra stuff here