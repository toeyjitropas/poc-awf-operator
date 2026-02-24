"""
auth.py
One-time login script using Device Code flow.
Run this once → saves tokens to token.json
After that, your app uses refresh_token silently forever after.
"""

import json
import logging
import structlog
import webbrowser
from dotenv import load_dotenv
import msal
from typing import List
import os
import yaml

with open('./credential.yaml', 'r') as file:
        data = yaml.safe_load(file)

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECERT_ID = os.getenv('CLIENT_SECERT_ID')

SCOPES = data['SCOPES']

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(format="%(message)s", level=logging.DEBUG)
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()

# ─────────────────────────────────────────────────────────────────────────────
MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'

# ──  Request Tokens 
def get_access_token(application_id: str,client_secret: str,scopes: List):
    client = msal.ConfidentialClientApplication(
        client_id=application_id,
        client_credential=client_secret,
        authority="https://login.microsoftonline.com/consumers/"
    )

    # Check refresh_token existance
    refresh_token = os.getenv('REFRESH_TOKEN')
    
    if refresh_token:
        # try to retrieved tokens
        token_response = client.acquire_token_by_refresh_token(refresh_token=refresh_token,scopes=scopes)
    else:
        auth_request_url = client.get_authorization_request_url(scopes)
        webbrowser.open(auth_request_url)
        authorization_code = input('put code: ')

        if not authorization_code:
            raise ValueError('Authorization code is empty')
        
        token_response = client.acquire_token_by_authorization_code(
            code=authorization_code,
            scopes=scopes
        )
    
    if 'access_token' in token_response:
        # Store access token
        log.info(token_response)
        return token_response['access_token']
    else:
        raise Exception('Fail to acquire token')

if __name__ == '__main__':
    
    log.info("Requesting Token")
    try:
        access_token = get_access_token(application_id=CLIENT_ID,client_secret=CLIENT_SECERT_ID,scopes=SCOPES)
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        log.info(f"{headers}")
    except Exception as e:
        log.info(f"Error : {e}")

