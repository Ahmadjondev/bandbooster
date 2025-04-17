from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find a user matching the username or email
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple users have the same email, get the first one
            user = User.objects.filter(
                Q(username=username) | Q(email=username)
            ).first()
            if user.check_password(password):
                return user
            return None
        return None
