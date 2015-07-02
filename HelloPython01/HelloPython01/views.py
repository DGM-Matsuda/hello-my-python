
__author__ = 'koichi.matsuda'

import os
import json
import httplib2
import configparser
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from django.http import HttpResponse
from django.shortcuts import render
from pprint import pprint


def home(request):

    config = configparser.ConfigParser()
    config.read('appconf.ini')

    return render(request, 'base.html', {'gid': config['DEFAULT']['GoogleClientID']})


def plus(request):

    gplus_id = ""
    config = configparser.ConfigParser()
    config.read('appconf.ini')
    CLIENT_ID = config['DEFAULT']['GoogleClientID']
    code = request.body
    pprint(code.decode("utf-8"))
    CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')
    pprint(CLIENT_SECRETS)

    try:
        oauth_flow = flow_from_clientsecrets(CLIENT_SECRETS, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code.decode("utf-8"))
        pprint(credentials)
    except FlowExchangeError:
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
    # アクセス トークンが、意図したユーザー用に使用されていることを確認します。
    # if result['user_id'] != gplus_id:
    #     response = HttpResponse(
    #         json.dumps("Token's user ID doesn't match given user ID."), 401)
    #     response['Content-Type'] = 'application/json'
    #     return response
    # アクセス トークンがこのアプリに対して有効であることを確認します。
    if result.get('issued_to') != CLIENT_ID:
        response = HttpResponse(
            json.dumps("Token's client ID does not match app's."), 401)
        response['Content-Type'] = 'application/json'
        return response
    stored_credentials = request.session.get('credentials')
    stored_gplus_id = request.session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = HttpResponse(json.dumps('Current user is already connected.'), 200)
        response['Content-Type'] = 'application/json'
        return response
    # アクセス トークンを後で使用するためにセッションで保存します。
    # request.session['credentials'] = credentials
    request.session['gplus_id'] = gplus_id
    response = HttpResponse(json.dumps('Successfully connected user.'), 200)
    return response