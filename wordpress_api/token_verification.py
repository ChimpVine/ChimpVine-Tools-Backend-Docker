import http.client
import json
from urllib.parse import urlparse

def api_request(auth_token, site_url, endpoint_suffix, Tool_ID,Token):
    """
    Helper function to perform API requests to the WordPress site.
    """
    # Parse the site URL
    parsed_url = urlparse(site_url if site_url.startswith("http") else f"https://{site_url}")
    domain, path = parsed_url.netloc, parsed_url.path.rstrip('/')

    if not auth_token or not domain:
        return {"status": "error", "message": "Authorization token and site URL are required"}
    
    # Set headers and payload
    headers = {
        'Authorization': f"Bearer {auth_token}",
        'Content-Type': 'application/json'
    }
    aitoolID = "1"
    payload = json.dumps({
        "AIToolID": Tool_ID,
        'TokenUsed': Token
    })

    try:
        # Create HTTPS connection and send request
        conn = http.client.HTTPSConnection(domain)
        endpoint = f"{path}/wp-json/teacher-tools/v1/{endpoint_suffix}"
        conn.request("POST", endpoint, payload, headers)
        
        response = conn.getresponse()
        response_data = response.read().decode()
        response_json = json.loads(response_data)
        print(f"Response Status: {response.status}")
        print(f"Response Data: {response_data}")
        # Handle response based on status code
        if response.status == 200 and response_json.get("success"):
            return {"status": "success", "message": response_json.get("message")}
        elif response.status in [400, 401, 403]:
            return {
                "status": "error",
                "message": response_json.get("message", "Authentication or permission error"),
                "code": response.status
            }
        else:
            return {"status": "error", "message": f"Unexpected Error. Status Code: {response.status}"}
    except Exception as e:
        print(f"Error calling WordPress API: {e}")
        return {"status": "error", "message": "Failed to connect to WordPress API"}

def verify_token(auth_token, site_url,Tool_ID,Token):
    """
    Function to verify the token using the WordPress API.
    """
    return api_request(auth_token, site_url, "check-token",Tool_ID,Token)

def use_token(auth_token, site_url,Tool_ID,Token):
    """
    Function to use (subtract) the token using the WordPress API.
    """
    if not Token:
        print("Error: TEST_TOKEN is not set in environment variables.")
        return {"status": "error", "message": "Missing TEST_TOKEN"}
    
    return api_request(auth_token, site_url, "use-token",Tool_ID,Token)

