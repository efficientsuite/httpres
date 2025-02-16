import subprocess
import requests

def request(request_data):
    auth_usage_details = ""
    # Proxy config
    proxy_data = request_data.get('proxy', {})
    if proxy_data and proxy_data.get('host'):
        selected_proxy = proxy_data
    else:
        selected_proxy = None
    proxy_url = None
    if selected_proxy:
        host = selected_proxy.get('host', '').strip()
        port = selected_proxy.get('port', '').strip()
        username = selected_proxy.get('username', '').strip()
        password = selected_proxy.get('password', '').strip()
        if host and port:
            if username and password:
                proxy_url = f"http://{username}:{password}@{host}:{port}"
            else:
                proxy_url = f"http://{host}:{port}"
    proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None

    # Auth config
    bearer_token = None
    auth_data = request_data.get('auth', {})

    active_tab = auth_data.get('active')

    # Basic Auth
    if active_tab == 'Basic':
        basic_data = auth_data.get('basic', {})
        if basic_data:
            username = basic_data.get('username')
            password = basic_data.get('password')
            bearer_token = f"{username}:{password}"

    # Bearer token
    if active_tab == 'Bearer':
        bearer_data = auth_data.get('bearer', {})
        if bearer_data:
            bearer_token = bearer_data.get('token')
    
    # Certificate 
    selected_certificate = None
    if active_tab == 'Certificate':
        cert_data = auth_data.get('certificate', {})
        if cert_data and cert_data.get('client_certificate'):
            selected_certificate = cert_data
        else:
            selected_certificate = None

    # OAuth 2.0
    if active_tab == 'OAuth 2.0':
        try:
            # For testing: https://oauth.tools/collection/1599045253169-GHF
            oauth_data = auth_data.get('oauth', {})
            bearer_token = None
            if oauth_data:
                token_url = oauth_data.get('token_url')
                grant_type = oauth_data.get('grant_type')
                client_id = oauth_data.get('client_id')
                client_secret = oauth_data.get('client_secret')
                scopes = " ".join(oauth_data.get('scopes'))
                if grant_type == "Client Credentials":
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    body = {
                        'grant_type': 'client_credentials',
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'scope': scopes
                    }
                    response = requests.post(
                        token_url, 
                        allow_redirects=True,
                        headers=headers,
                        data=body
                    )
                    # if response.status_code == 301 or response.status_code == 302:
                    #     redirect_url = response.headers.get('Location')
                    #     response = requests.post(redirect_url, data={
                    #         'grant_type': 'client_credentials',
                    #         'client_id': client_id,
                    #         'client_secret': client_secret,
                    #         'scope': 'read%20write%20openid'
                    #     })
                    response_data = response.json()
                    bearer_token = response_data.get('access_token')
                    if len(bearer_token) > 0:
                        auth_usage_details = "OAuth: Client Credentials -> Access token retrieved ✅"
                        #auth_usage_details += f"\nBody: {body}"
                    else:
                        auth_usage_details = "OAuth: Client Credentials -> Access token retrieval failed ❌"
        except Exception as e:
            if e and e.msg:
                error_object = {'stdout':'', 'stderr': str(e.msg)}
                return '0', error_object, None
            else:
                error_object = {'stdout':'', 'stderr': 'Unknown error'}
                return '0', error_object, None

    # Prepare the curl command
    curl_command = []
    use_system_curl = True
    try:
        subprocess.run(["lib/curl/bin/curl", "--version"], capture_output=True, text=True)
        use_system_curl = False
    except FileNotFoundError:
        print("lib/curl/bin/curl not found. Using system curl instead.")

    if use_system_curl:
        curl_command.extend(["curl", "-X", request_data['method'], request_data['url'], "--data", request_data['body'], "--http1.1", "-v"])
    else:
        curl_command.extend(["lib/curl/bin/curl", "-X", request_data['method'], request_data['url'], "--data", request_data['body'], "--http1.1", "-verbose"])

    headers_list = request_data['headers'].splitlines()
    if not any(header.lower().startswith('user-agent') for header in headers_list):
        curl_command.extend(["-H", "User-Agent: httpRes/1.0.0"])
    for header in headers_list:
        curl_command.extend(["-H", header])
    if bearer_token:
        curl_command.extend(["-H", f"Authorization: Bearer {bearer_token}"])
    if proxies:
        curl_command.extend(["--proxy", proxy_url])
    if selected_certificate:
        curl_command.extend([
            "--cacert", selected_certificate['ca_certificate'],
            "--cert", selected_certificate['client_certificate'],
            "--key", selected_certificate['private_key'],
            "--pass", selected_certificate['private_key_password']
        ])
        if cert_data and cert_data['verify'] == False:
            curl_command.extend(["--insecure"])

    # Add the option to output the HTTP status code
    curl_command.extend(["-w", "%{http_code}"])

    # Add the option to remove performance metrics -s, --silent
    curl_command.extend(["-s"])

    result = subprocess.run(curl_command, capture_output=True, text=True)
    response_code = result.stdout[-3:]  # Extract the last 3 characters which are the HTTP status code
    result.stdout = result.stdout[:-3]  # Remove the status code from the output
    return response_code, result, auth_usage_details, curl_command

