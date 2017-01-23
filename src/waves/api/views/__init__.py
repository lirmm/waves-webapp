""" WAVES API views """
from __future__ import unicode_literals

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.conf import settings
from profiles.auth import APIKeyAuthBackend


class WavesBaseView(APIView):
    """ Base WAVES API view, set up for all subclasses permissions / authentication """
    authentication_classes = (APIKeyAuthBackend, SessionAuthentication)
    permission_classes = [IsAuthenticated, ]

    def get_permissions(self):
        if settings.DEBUG:
            self.permission_classes = [AllowAny,]
        return super(WavesBaseView, self).get_permissions()

