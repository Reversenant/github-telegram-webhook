import requests
import os

TEMPLATES_PATH = os.getenv('TEMPLATES_PATH', './templates.example')

WEBHOOK_DEFS = "https://octokit.github.io/webhooks/payload-examples/api.github.com/index.json"

ACTION_EVENT = '''"{0}" %}}
    User <code>{{{{ data['sender']['login'] }}}}</code> triggered <i>{1}-{{{{ data['action'] }}}}</i> on <a href="https://github.com/{{{{ data['repository']['full_name'] }}}}">{{{{ data['repository']['full_name'] }}}}</a> repo.
'''

if __name__ == "__main__":
    for event in requests.get(WEBHOOK_DEFS).json():
        with open(f"./{TEMPLATES_PATH}/{event['name']}.j2", 'w') as f:
            f.write("{% if data['action']==")
            for idx, action in enumerate(event['actions']):
                if idx != 0:
                    f.write("{% elif data['action']==")
                f.write(ACTION_EVENT.format(action, event['name']))
            f.write(end='{% endif %}')
