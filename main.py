import jinja2
import os
import hmac
from hashlib import sha256
import requests
import json
import logging

# Names of repositories and ID topics from telegram chat
REPO_TOPIC_MAP = {
    "first repository": 1,
    "second repository": 2 
}

def verify_github_signature(secret, signature, payload):
    mac = hmac.new(secret.encode(), msg=payload.encode(), digestmod=sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)

def createMessage(gh_event: str, body: str) -> str:
    templateLoader = jinja2.FileSystemLoader(searchpath='./templates')
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(f'{gh_event}.j2')
    text = template.render(data=json.loads(body))
    logging.debug(f"Event: {gh_event}, text: {text}")
    return text


def sendMessage(text: str, thread_id: int = None) -> dict:
    payload = {
        "text": text,
        "parse_mode": 'markdown',
        "chat_id": os.environ['CHAT_ID'],
    }
    if thread_id:
        payload["message_thread_id"] = thread_id

    logging.debug(f"TG Payload: {payload}")
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    r = requests.post(
        f'https://api.telegram.org/bot{os.environ["BOT_TOKEN"]}/sendMessage', json=payload, headers=headers)
    if r.status_code != 200:
        err = {'statusCode': r.status_code, 'body': r.text}
        logging.error(err)
        return err
    return {'statusCode': 200, 'body': 'Translated to receivers'}

def returnHandler(resp):
    logging.info(resp)
    return resp

def ya_handler(event, context):
    logging.getLogger().setLevel(logging.DEBUG)

    if event['httpMethod'] != "POST":
        logging.debug(f"HTTP Method is {event['httpMethod']}")
        return returnHandler({'statusCode': 405, 'body': 'Method Not Allowed'})

    if not event['headers'].get('User-Agent', '').startswith("GitHub-Hookshot"):
        logging.debug(f"User-Agent is {event['headers'].get('User-Agent')}")
        return returnHandler({'statusCode': 403, 'body': 'Forbidden: Invalid User-Agent'})

    required_env_vars = ['CHAT_ID', 'BOT_TOKEN', 'GITHUB_SECRET']
    missing_env_vars = [var for var in required_env_vars if var not in os.environ]
    if missing_env_vars:
        return returnHandler({'statusCode': 500, 'body': f'Missing environment variables: {", ".join(missing_env_vars)}'})

    signature = event['headers'].get('X-Hub-Signature-256')
    if not signature:
        logging.debug("Missing X-Hub-Signature-256")
        return returnHandler({'statusCode': 403, 'body': 'Forbidden: Missing signature'})
    
    if not verify_github_signature(os.environ['GITHUB_SECRET'], signature, event['body']):
        logging.debug("Invalid signature")
        return returnHandler({'statusCode': 403, 'body': 'Forbidden: Invalid signature'})

    payload = json.loads(event['body'])
    repository_name = payload['repository']['name']

    thread_id = REPO_TOPIC_MAP.get(repository_name)
    if not thread_id:
        logging.debug(f"No topic mapping found for repository: {repository_name}")
        return returnHandler({'statusCode': 400, 'body': 'Bad Request: No topic mapping for repository'})

    text = createMessage(event['headers']['X-Github-Event'], event['body'])
    return returnHandler(sendMessage(text, thread_id))