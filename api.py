import requests
import base64
import json

"""
Helper class to handle authentication
"""

class MakeLeapsAPI:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    """ Authenticates Client """
    # Returns access token
    def _auth_client(self):
        url = 'https://api-meetup.makeleaps.com/user/oauth2/token/'

        creds = f'{self.client_id}:{self.client_secret}'.encode('utf-8')
        creds_encoded = base64.b64encode(creds).decode('utf-8')

        headers = {'Authorization': f'Basic {creds_encoded}'}
        data = {'grant_type': 'client_credentials'}

        response = requests.post(url, data=data, headers=headers)
        response_json = response.json()

        return response_json['access_token']

    """ Make authenticated POST requests to API """
    # The API will check if Bearer token in request is valid,
    # and if so authenticate the request
    def post(self, token, url, data):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers)

        return (response.status_code, response.json()['response'])

    """ Make authenticated GET requests to API """
    def get(self, token, url):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url, headers=headers)

        return (response.status_code, response.json()['response'])

    # TODO: Figure out correct header format
    """ Make authenticated PUT request for uploading PDF """
    def put(self, token, url):
        headers = {
            'Content-Type': 'application/pdf',
            'Authorization': f'Bearer {token}',
        }
        response = requests.put(url, headers=headers)

        return (response.status_code, response.json()['response'])
