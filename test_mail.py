"""
test_emails.py
Uses saved token.json to fetch your emails.
Run auth.py first to get a fresh token.
"""

import httpx
import json
import logging
import structlog
import sys
from pathlib import Path
from auth import get_access_token, MS_GRAPH_BASE_URL
import yaml

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

with open('./credential.yaml', 'r') as file:
        data = yaml.safe_load(file)

CLIENT_ID = data['CLIENT_ID']
CLIENT_SECERT_ID = data['CLIENT_SECERT_ID']
SCOPES = data['SCOPES']

print(CLIENT_ID)

def fetch_emails():
    endpoint = f'{MS_GRAPH_BASE_URL}/me/messages'

    try:
        access_token = get_access_token(
            application_id=CLIENT_ID,
            client_secret=CLIENT_SECERT_ID,
            scopes=SCOPES
        )
        log.info('Get Access Token')
        headers = {
            'Authorization': 'Bearer ' + access_token
        }

        print(access_token)

        log.info('Staring Fecthing Email')
        for i in range(0,4,2):
            params = {
                '$top': 2,
                '$select': '*',
                '$skip': i,
                '$orderby': 'receivedDateTime desc'
            }
            response = httpx.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                raise Exception(f' Fail to get mail: {response.text}')
            
            json_response = response.json()
            log.info(json_response)

    except httpx.HTTPStatusError as e:
        log.info(f'{e}')
    except Exception as e:
        log.info(f'Error : {e}')

if __name__ == '__main__':
    fetch_emails()