import jinja2
import os
import hmac
from hashlib import sha256
import requests
import json


def _verify_signature(secret: bytes, sig: str, msg: bytes) -> bool:
    mac = hmac.new(secret, msg=msg, digestmod=sha256)
    return hmac.compare_digest(mac.hexdigest(), sig)


def createMessage(gh_event: str, body: str) -> str:
    templateLoader = jinja2.FileSystemLoader(
        searchpath=os.environ['TEMPLATES_PATH'])
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(f'{gh_event}.j2')
    return template.render(data=json.loads(body))


def sendMessage(text: str) -> dict:
    payload = {
        "text": text,
        "parse_mode": "HTML",
        "chat_id": os.environ['CHAT_ID'],
        "reply_to_message_id": os.environ.get('THREAD_ID','')
    }
    print(payload)
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    r = requests.post(
        f'https://api.telegram.org/bot{os.environ["BOT_TOKEN"]}/sendMessage', json=payload, headers=headers)
    if r.status_code != 200:
        return {'statusCode': r.status_code, 'body': r.text}
    return {'statusCode': 200, 'body': 'Translated to recievers'}

# Special function to YC Cloud Functions


def ya_handler(event, context):
    if event['httpMethod'] != "POST":
        return {'statusCode': 405}
    if not "GitHub-Hookshot" in event['headers']['User-Agent']:
        return {'statusCode': 403}
    if 'WEBHOOK_SECRET' in os.environ:
        if not 'X-Hub-Signature-256' in event['headers']:
            return {'statusCode': 403, 'body': 'Webhook signature is missing'}
        gh_signature = event['headers']['X-Hub-Signature-256']
        if not _verify_signature(
            os.environ['WEBHOOK_SECRET'].encode('utf-8'),
            gh_signature.split('=')[1],
            event['body'].encode('utf-8')
        ):
            return {'statusCode': 403, 'body': 'Webhook signature is wrong'}
    if not ('CHAT_ID' in os.environ or 'BOT_TOKEN' in os.environ or 'TEMPLATES_PATH' in os.environ):
        return {'statusCode': 500, 'body': 'Some settings is missing'}
    text = createMessage(event['headers']['X-Github-Event'], event['body'])
    return sendMessage(text)
