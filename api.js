//import axios from 'axios';
const axios = require('axios').default;
// necessary for using x-www-form-urlencoded format for OAuth2
const querystring = require('querystring');

/**
 * Helper class to handle authentication and API calls
 */
class MakeLeapsAPI
{
  constructor(client_id, client_secret) {
    this.client_id = client_id;
    this.client_secret = client_secret;
    this.token = null;
  }

  /**
   * Authenticate Client and retrieve an access token
   */
  auth_client() {
      const creds_encoded = Buffer.from(`${this.client_id}:${this.client_secret}`, 'utf8')
                                  .toString('base64');

      const url = 'https://api-meetup.makeleaps.com/user/oauth2/token/';
      const data = {'grant_type': 'client_credentials'};
      const options = {
        headers: {
          'Authorization': `Basic ${creds_encoded}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      };

      return axios.post(url, querystring.stringify(data), options)
                  .then(response => {
                    this.token = response.data.access_token
                  })
                  .catch(error => {
                    console.log(error.response.data)
                  });
  }

  /**
   * Make authenticated POST request and return response
   */
  post(url, data) {
    const options = {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    };

    return axios.post(url, data, options)
                .then(response => {
                  return response
                })
                .catch(error => {
                  console.log(error.response.data)
                });
  }

  /**
   * Make authenticated GET request and return response
   */
  get(url) {
    const options = {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    };

    return axios.get(url, options)
                .then(response => {
                  return response
                })
                .catch(error => {
                  console.log(error.response.data)
                });
  }

  /**
   * Make authenticated PUT request and return response
   */
  put(url, filename) {
    const options = {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    };

    return axios.put(url, data, options)
                .then(response => {
                  return response
                })
                .catch(error => {
                  console.log(error.response.data)
                });
  }
}

module.exports = MakeLeapsAPI;
