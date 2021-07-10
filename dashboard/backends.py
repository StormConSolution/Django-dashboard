from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
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

class CaseInsensitiveModelBackend(BaseBackend):
    
    def authenticate(self, request, username, password):
        UserModel = get_user_model()
        if username is None:
            return None
        try:
            d = {'%s__iexact' % UserModel.USERNAME_FIELD: username}
            user = UserModel.objects.get(**d)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass

        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
