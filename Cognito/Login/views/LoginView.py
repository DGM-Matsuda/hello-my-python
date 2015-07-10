from django.shortcuts import redirect
from django.views.generic import TemplateView
from Cognito import settings

__author__ = 'koich_000'


class LoginView(TemplateView):

    template_name = 'Login/index.html'

    def get(self, request, *args, **kwargs):
        cognito_id = request.session.get('IdentityId')
        if cognito_id is not None:
            return redirect('/')
        return super(LoginView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # コンテキストを取得するために、先に基底クラスの機能を呼び出します。
        context = super(LoginView, self).get_context_data(**kwargs)
        # 全書籍のクエリセットを追加します。
        context['LANGUAGE_CODE'] = settings.LANGUAGE_CODE
        return context
