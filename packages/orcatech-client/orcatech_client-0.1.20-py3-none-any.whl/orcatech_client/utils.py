import os
from dotenv import load_dotenv

load_dotenv()

def get_host_and_token():
    host = os.getenv("HOST_URL")
    auth_token = os.getenv("AUTH_TOKEN")
    
    if not host or not auth_token:
        raise ValueError("Please set the HOST_URL and AUTH_TOKEN environment variables.")
    return host, auth_token