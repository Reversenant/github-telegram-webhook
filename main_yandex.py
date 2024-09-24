import jinja2
import os
import hmac
from hashlib import sha256
import requests
import json
import logging
import re

REPO_TOPIC_MAP = {
    "Test-repo": {"topics": ["-123"], "template_set": "default_set"}
}

def verify_github_signature(secret, signature, payload):
    mac = hmac.new(secret.encode(), msg=payload.encode(), digestmod=sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)

def createMessage(repository_name: str, gh_event: str, body: str) -> str:
    template_set = REPO_TOPIC_MAP[repository_name]["template_set"]
    templateLoader = jinja2.FileSystemLoader(searchpath=f'./templates/{template_set}')
    templateEnv = jinja2.Environment(loader=templateLoader)
    try:
        template = templateEnv.get_template(f'{gh_event}.j2')
    except jinja2.TemplateNotFound:
        logging.error(f"Template {gh_event}.j2 not found for repository {repository_name} in set {template_set}")
        return ''
    text = template.render(data=json.loads(body))
    logging.debug(f"Repository: {repository_name}, Event: {gh_event}, text: {text}")
    return text

def extract_and_clean_urls(text: str) -> tuple:
    file_urls = re.findall(r'https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/assets\/[a-zA-Z0-9_-]+\/[a-f0-9-]+', text)
    clean_text = re.sub(r'!\[.*?\]\(https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/assets\/[a-zA-Z0-9_-]+\/[a-f0-9-]+\)( )*\r\n', '', text, count=1)
    clean_text = clean_text.replace("![", "[")
    return clean_text, file_urls

def sendMessage(text: str, image_urls, chat_id: str, thread_id: int = None) -> dict:
    data = {
        "parse_mode": 'markdown',
        "chat_id": chat_id,
        "caption": text if image_urls else None,
        "text": text if not image_urls else None,
        "message_thread_id": thread_id
    }
    url = f'https://api.telegram.org/bot{os.environ["BOT_TOKEN"]}/send{"Photo" if image_urls else "Message"}'
    files = {'photo': requests.get(image_urls).content} if image_urls else None
    response = requests.post(url, data=data, files=files) if image_urls else requests.post(url, json=data)

    if response.status_code != 200:
        err = {'statusCode': response.status_code, 'body': response.text}
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

    if repository_name not in REPO_TOPIC_MAP:
        logging.debug(f"No topic mapping found for repository: {repository_name}")
        return returnHandler({'statusCode': 400, 'body': 'Bad Request: No topic mapping for repository'})

    text = createMessage(repository_name, event['headers']['X-Github-Event'], event['body'])
    text, file_urls = extract_and_clean_urls(text)

    responses = []
    for mapping in REPO_TOPIC_MAP[repository_name]["topics"]:
        chat_id, topic_id = mapping.split(':') if ':' in mapping else (mapping, None)
        responses.append(sendMessage(text, file_urls[0] if file_urls else None, chat_id, topic_id))

    return returnHandler(responses)
