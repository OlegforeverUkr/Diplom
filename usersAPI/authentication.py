from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from django.conf import settings


class CustomAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        user = token.user
        token.last_activity = timezone.now()
        token.save()

        if not user.is_staff or not user.is_superuser:
            if token.last_activity < timezone.now() - timezone.timedelta(minutes=settings.TOKEN_EXPIRED_MINUTES):
                token.delete()
                raise exceptions.AuthenticationFailed(_('Token has expired!!!'))

        return (user, token)