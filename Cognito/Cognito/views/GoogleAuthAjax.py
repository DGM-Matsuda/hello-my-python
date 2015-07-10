# -*- coding: utf-8 -*-

import configparser
import os
import json
import boto3
import httplib2
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.http import HttpResponse
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from Cognito import settings


class GoogleAuthAjax(View):

    APP_CONF_INI = 'appconf.ini'
    CLIENT_SECRETS_JSON = 'client_secrets.json'

    def get_google_client_id(self):

        try:
            path = os.path.join(settings.BASE_DIR, self.APP_CONF_INI)
            config = configparser.ConfigParser()
            config.read(path)
            return config['DEFAULT']['GoogleClientID']
        except FileNotFoundError:
            raise

    def get_google_client_secrets_path(self):

        path = os.path.join(settings.BASE_DIR, self.CLIENT_SECRETS_JSON)
        if os.path.exists(path):
            return path
        else:
            raise FileNotFoundError()

    def get_aws_cognito_identitypool_id(self):
        try:
            path = os.path.join(settings.BASE_DIR, self.APP_CONF_INI)
            config = configparser.ConfigParser()
            config.read(path)
            return config['DEFAULT']['IdentityPoolId']
        except FileNotFoundError:
            raise

    def get_aws_cognito_account_id(self):
        try:
            path = os.path.join(settings.BASE_DIR, self.APP_CONF_INI)
            config = configparser.ConfigParser()
            config.read(path)
            return config['DEFAULT']['CognitoAccountId']
        except FileNotFoundError:
            raise


    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(GoogleAuthAjax, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        code = request.body

        client_id = self.get_google_client_id()
        client_secrets = self.get_google_client_secrets_path()

        try:
            oauth_flow = flow_from_clientsecrets(client_secrets, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code.decode("utf-8"))
        except FlowExchangeError as e:
            response = HttpResponse(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response['Content-Type'] = 'application/json'
            return response

        # アクセス トークンの有効性をチェックします。
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        res, content = h.request(url, 'GET')
        result = json.loads(content.decode("utf-8"))

        # トークン情報にエラーがあれば、中断します。
        if result.get('error') is not None:
            response = HttpResponse(json.dumps(result.get('error')), 500)
            response['Content-Type'] = 'application/json'
            return response

        # アクセス トークンがこのアプリに対して有効であることを確認します。
        if result.get('issued_to') != client_id:
            response = HttpResponse(
                json.dumps("Token's client ID does not match app's."), 401)
            response['Content-Type'] = 'application/json'
            return response

        client = boto3.client(
            service_name='cognito-identity',
            region_name='us-east-1'
        )

        cognitoId = client.get_id(
            AccountId=self.get_aws_cognito_account_id(),
            IdentityPoolId=self.get_aws_cognito_identitypool_id(),
            Logins={
                'accounts.google.com': credentials.token_response.get('id_token')
            }
        )

        request.session['IdentityId'] = cognitoId.get('IdentityId')

        response = HttpResponse(json.dumps('Successfully connected user.'), 200)
        response['Content-Type'] = 'application/json'
        return response

