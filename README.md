# github-telegram-webhook
Webhook to receive events from GitHub

## How to run
1. Rename `.env.example` and provide required environment variables
2. Rename `templates.example` according to `TEMPLATES_PATH` environment variable
3. Provide code to Yandex Cloud Cloud Function (handler - `main.ya_handler`) or create your own one deploy with public URL.
4. Set up webhook in your repository. Choose events carefully. 

## Message templates
Messages templates -- pure Jinja2 templates for creating message to Telegram. Every template is targeted to one of webhook events (`x-github-event` header) with number of actions. 
`templates.example` is generated by `generate_templates.py`, list of events provided by [official webhook specification](https://github.com/octokit/webhooks) 

## Helpers
Helpers are special folder for templates enhancements.  
Helper functions has special naming declaration:
* Helpers are located in `helpers/` directory
* One helper function - one python file 
* Helper function name = Python file name
Webhook tries to load all helper functions on start and provide functions to jinja2 Environment.
You will free to provide your own helpers on specific deploy without changing main webhook code repo, like templates.

## Tips and tricks
1. Filter sending events. `x-github-event` can be filtered by GitHub Webhook settings. Each action of event can be filtered by remove `if` statement for this action in specified event template.