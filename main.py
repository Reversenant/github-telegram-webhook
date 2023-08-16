import jinja2
import os
import hmac
from hashlib import sha256
import requests
import json
import logging
import importlib
import pkgutil

def get_helpers() -> dict:
    func_dict = {}
    try:
        i = importlib.import_module("helpers")
        for m in pkgutil.iter_modules(i.__path__):
            func_dict[m.name] = getattr(importlib.import_module(f"helpers.{m.name}"), m.name)
    except:
        logging.error("There is no helpers in project")
    return func_dict

def _verify_signature(secret: bytes, sig: str, msg: bytes) -> bool:
    mac = hmac.new(secret, msg=msg, digestmod=sha256)
    macdigest = mac.hexdigest()
    logging.debug(f"Compare digest {macdigest} and sig {sig}")
    return hmac.compare_digest(macdigest, sig)

def createMessage(gh_event: str, body: str) -> str:
    templateLoader = jinja2.FileSystemLoader(
        searchpath=os.environ['TEMPLATES_PATH'])
    templateEnv = jinja2.Environment(loader=templateLoader)
    templateEnv.globals.update(get_helpers())
    template = templateEnv.get_template(f'{gh_event}.j2')
    text = template.render(data=json.loads(body))
    logging.debug(f"Event: {gh_event}, text: {text}")
    return text

def sendMessage(text: str) -> dict:
    payload = {
        "text": text,
        "parse_mode": "HTML",
        "chat_id": os.environ['CHAT_ID'],
        "reply_to_message_id": os.environ.get('THREAD_ID','')
    }
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
    return {'statusCode': 200, 'body': 'Translated to recievers'}

# Special function to YC Cloud Functions

def returnHandler(resp):
    logging.info(resp)
    return resp

def ya_handler(event, context):
    logging.getLogger().setLevel(logging.DEBUG)
    if event['httpMethod'] != "POST":
        logging.debug(f"HTTP Method is {event['httpMethod']}")
        return returnHandler({'statusCode': 405})
    if not "GitHub-Hookshot" in event['headers']['User-Agent']:
        logging.debug(f"User-Agent is {event['headers']['User-Agent']}")
        return returnHandler({'statusCode': 403})
    if 'WEBHOOK_SECRET' in os.environ:
        if not 'X-Hub-Signature-256' in event['headers']:
            return returnHandler({'statusCode': 403, 'body': 'Webhook signature is missing'})
        gh_signature = event['headers']['X-Hub-Signature-256']
        if not _verify_signature(
            os.environ['WEBHOOK_SECRET'].encode('utf-8'),
            gh_signature.split('=')[1],
            event['body'].encode('utf-8')
        ):
            return returnHandler({'statusCode': 403, 'body': 'Webhook signature is wrong'})
    if not ('CHAT_ID' in os.environ or 'BOT_TOKEN' in os.environ or 'TEMPLATES_PATH' in os.environ):
        return returnHandler({'statusCode': 500, 'body': 'Some settings is missing'})
    text = createMessage(event['headers']['X-Github-Event'], event['body'])
    return returnHandler(sendMessage(text))