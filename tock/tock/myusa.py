from social.backends.oauth import BaseOAuth2
import requests

class MyusaOAuth2(BaseOAuth2):
    """ MyUSA OAuth Authentication Backend"""
    name = 'myusa'
    #PROVIDER_BASE_URL = 'http://localhost:3001'
    PROVIDER_BASE_URL = 'https://alpha.my.usa.gov'
    AUTHORIZATION_URL = PROVIDER_BASE_URL + '/oauth/authorize'
    ACCESS_TOKEN_URL = AUTHORIZATION_URL
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    STATE_PARAMETER = None
    ID_KEY = 'uid'

    def get_user_details(self, response):
        """ Return user details from MyUSA account """
        return {
            'uid': response.get('uid'),
            'email': response.get('email'),
        }

    def user_data(self, access_token, *args, **kwargs):
        """ Loads user profile from MyUSA """
        try:
            r = requests.get(self.PROVIDER_BASE_URL + '/api/profile', headers={'Authorization': ' '.join(['Bearer', access_token]), 'Content-Type': 'application/json'})
            print(r.request.url)
            print(r.request.headers)
            print(r.text)
            return r.json()
        except ValueError:
            return None