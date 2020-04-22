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

    def auth_client(self):
        """ Authenticate Client and return an access token """

        url = 'https://api-meetup.makeleaps.com/user/oauth2/token/'

        creds = f'{self.client_id}:{self.client_secret}'.encode('utf-8')
        creds_encoded = base64.b64encode(creds).decode('utf-8')

        headers = {'Authorization': f'Basic {creds_encoded}'}
        data = {'grant_type': 'client_credentials'}

        response = requests.post(url, data=data, headers=headers)
        response_json = response.json()

        return response_json['access_token']

    def post(self, token, url, data):
        """ Make authenticated POST request
        and return response status and data """

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        data = json.dumps(data)
        response = requests.post(url, data=data, headers=headers)

        return (response.status_code, response.json()['response'])

    def get(self, token, url):
        """ Make authenticated GET request
         and return response status and data """

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url, headers=headers)

        return (response.status_code, response.json()['response'])

    # can't use this because POST requests not accepted
    def upload_pdf_wrong(self, token, url, filename):
        """ Make authenticated POST request for uploading PDF
        and return response status """

        files = {
            "file": (f'{filename}',
                    open(f'{filename}', 'rb'),
                    "application/pdf",
                    {'Authorization': f'Bearer {token}'})
        }
        response = requests.post(url, files=files)
        print(response.raise_for_status())

        return (response.status_code)

    # TODO: Figure out what is still wrong
    # "response":{"content_file":["No file was submitted"]} -> Why?
    def upload_pdf(self, token, url, filename):
        """ Make authenticated POST request for uploading PDF
        and return response status """
        
        headers = {
            'Content-Type': 'multipart/form-data',
            'Authorization': f'Bearer {token}',
        }
        response = requests.put(url, data=open(f'{filename}', 'rb'), headers=headers)

        return(response.status_code)
