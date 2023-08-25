import requests
import os

# Only 2 supported: markdown or HTLM
MSG_FORMAT = os.getenv('MSG_FORMAT', 'markdown')
TEMPLATES_PATH = os.getenv('TEMPLATES_PATH', f'./{MSG_FORMAT}_templates.example')

WEBHOOK_DEFS = "https://octokit.github.io/webhooks/payload-examples/api.github.com/index.json"

ACTION_EVENT_HTML = '''"{0}" %}}
    User <code>{{{{ data['sender']['login'] }}}}</code> triggered <i>{1}-{{{{ data['action'] }}}}</i> on <a href="https://github.com/{{{{ data['repository']['full_name'] }}}}">{{{{ data['repository']['full_name'] }}}}</a> repo.
'''

ACTION_EVENT_MARKDOWN = '''
    User `{{{{ data['sender']['login'] }}}}` triggered *{1}-{{{{ data['action'] }}}}* on [{{{{ data['repository']['full_name'] }}}}](https://github.com/{{{{ data['repository']['full_name'] }}}}) repo.
'''

if __name__ == "__main__":
    action_event = ''
    if MSG_FORMAT == 'markdown':
        action_event = ACTION_EVENT_MARKDOWN
    elif MSG_FORMAT == 'HTML':
        action_event = ACTION_EVENT_HTML
    else:
        raise Exception("MSG_FORMAT is empty")
    for event in requests.get(WEBHOOK_DEFS).json():
        with open(f"./{TEMPLATES_PATH}/{event['name']}.j2", 'w') as f:
            f.write("{% if data['action']==")
            for idx, action in enumerate(event['actions']):
                if idx != 0:
                    f.write("{% elif data['action']==")
                f.write(action_event.format(action, event['name']))
            f.write('{% endif %}')
