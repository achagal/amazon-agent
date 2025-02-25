import requests
import os
from dotenv import load_dotenv
from dotenv import set_key

def refresh_access_token():
    # Load current environment variables
    load_dotenv()
    
    # Get credentials from environment variables
    refresh_token = os.getenv('AMAZON_REFRESH_TOKEN')
    client_id = os.getenv('AMAZON_CLIENT_ID')
    client_secret = os.getenv('AMAZON_CLIENT_SECRET')
    
    # API endpoint
    url = "https://api.amazon.com/auth/o2/token"
    
    # Request parameters
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        new_access_token = data['access_token']
        
        # Update the .env file with the new access token
        env_file_path = '.env'
        set_key(env_file_path, 'AMAZON_ACCESS_TOKEN', new_access_token, quote_mode="never") # remove quote mode = never if it doesn't work
        
        print("Access token successfully updated!")
        return new_access_token
        
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        return None

if __name__ == "__main__":
    refresh_access_token()
