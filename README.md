# github-telegram-webhook
Webhook to receive events from GitHub

## How to run
1. Rename `.env.example` and provide required environment variables.
3. Provide code to Yandex Cloud Cloud Function (handler - `main.ya_handler`) or create your own one deploy with public URL.
4. Set up webhook in your repository. Choose events carefully.
5. Modify `REPO_TOPIC_MAP` in the code - specify the names of repositories and the IDs of chat topics where you want to receive notifications.

## Message templates
Messages templates -- pure Jinja2 templates for creating message to Telegram. Every template is targeted to one of webhook events (`x-github-event` header). 
In the `templates` you can write your own templates. The list of events is provided in the [official webhook specification](https://github.com/octokit/webhooks)

## Tips and tricks
1. Filter sending events. `x-github-event` can be filtered by GitHub Webhook settings. Each action of event can be filtered by remove `if` statement for this action in specified event template.