from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class GuestBackend(BaseBackend):

    def authenticate(self, request, username, password=None):
        if username == 'guest@repustate.com':
            return User.objects.get(username='guest@repustate.com')
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
