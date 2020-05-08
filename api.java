import java.util.Base64;
import java.util.Scanner;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;

/**
 * Helper class to handle authentication and API calls
 */
public class MakeLeapsAPI{

  private String client_id;
  private String client_secret;
  private String token;

  public MakeLeapsAPI(String client_id, String client_secret) {
    this.client_id = client_id;
    this.client_secret = client_secret;
    auth_client();
  }

  /**
   * Authenticate Client and retrieve an access token
   */
  private void auth_client() {
    String url = 'https://api-meetup.makeleaps.com/user/oauth2/token/';
    String creds = this.client_id + ':' + this.client_secret; //encode utf-8?
    String creds_encoded = Base64.getEncoder().encodeToString(creds.getBytes());

    headers = {'Authorization': f'Basic {creds_encoded}'}
    data = {'grant_type': 'client_credentials'}

    response = requests.post(url, data=data, headers=headers)
    response_json = response.json()

    self.token = response_json['access_token']
  }

  /**
   * Pass token into header
   */
  private authorize_header() {
    return {'Authorization': f'Bearer {self.token}'};
  }

  /**
   * Make authenticated POST request and return response status and data
   */
  public String post(String url, NameValuePair data) {
    CloseableHttpClient client = HttpClients.createDefault();
    HttpPost post = new HttpPost(url);

    post.addHeader('Authorization': 'Bearer ' + this.token);
    post.addHeader('Content-Type', 'application/json');
    post.setRequestBody(data);

    HttpResponse httpresponse = httpclient.execute(post);

    Scanner sc = new Scanner(httpresponse.getEntity().getContent());

    return response.status_code, response.json()['response']
  }

  /**
   * Make authenticated GET request and return response status and data
   */
  public String get(String url) {
    headers = self._authorize_header()
    headers['Content-Type'] = 'application/json'

    response = requests.get(url, headers=headers)

    return response.status_code, response.json()['response']

    CloseableHttpClient httpclient = HttpClients.createDefault();
    HttpPost post = new HttpGet(url);
    HttpResponse httpresponse = httpclient.execute(httppost);
    Scanner sc = new Scanner(httpresponse.getEntity().getContent());
    return httpresponse.getStatusLine();
  }

  /**
   * Make authenticated PUT request and return response status and data
   */
  public String put(String url, String filename) {
    headers = self._authorize_header()

    files = {}
    if filename:
        files['content_file'] = open(f'{filename}', 'rb')

    response = requests.put(url, files=files, headers=headers)

    return response.status_code, response.json()['response']
  }
}
