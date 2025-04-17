from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_google_user = models.BooleanField(default=False)
    coins = models.IntegerField(default=0)  # Added coin balance

    def __str__(self):
        return self.user.email

# Signal to create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile when a user is created or updated.
    This ensures every user has a profile.
    """
    if created:
        # Only create a new profile if one doesn't already exist
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Make sure the profile exists even for existing users
        UserProfile.objects.get_or_create(user=instance)
