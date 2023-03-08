
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serzs import (
    UserSrzr,
    AuthTokenSRZ,
    )


class CreateUserViewSRZ(generics.CreateAPIView):
    """ Srsz: Create a new user in the system """
    serializer_class = UserSrzr


class CreateTokenView(ObtainAuthToken):
    """ Create a new auth token for user. """
    serializer_class = AuthTokenSRZ
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated user """
    serializer_class = UserSrzr
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """ Retrieve and return the authenticated user. """
        return self.request.user
