from django.shortcuts import redirect
from django.views.generic import View
from Cognito import settings

__author__ = 'koich_000'


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        request.session['IdentityId'] = None
        return redirect('/login')

