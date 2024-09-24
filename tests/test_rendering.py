import os
import sys
import json
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main_local import REPO_TOPIC_MAP, createMessage, extract_and_clean_urls, sendMessage

def test_rendering():
    logging.getLogger().setLevel(logging.DEBUG)

    test_cases = [
        ('issue_comment', 'tests/payloads/issue_comment/issue_comment_test_1.json'),
        ('issues', 'tests/payloads/issues/issues_test_1.json'),
        ('issues', 'tests/payloads/issues/issues_test_2.json'),
        ('pull_request', 'tests/payloads/pull_request/pull_request_test_1.json'),
        ('push', 'tests/payloads/push/push_test_1.json'),
        ('release', 'tests/payloads/release/release_test_1.json'),
        ('release', 'tests/payloads/release/release_test_2.json')
    ]

    for gh_event, payload_file in test_cases:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)

        repository_name = payload['repository']['name']

        if repository_name in REPO_TOPIC_MAP:
            template_set = REPO_TOPIC_MAP[repository_name]["template_set"]
            topics = REPO_TOPIC_MAP[repository_name]["topics"]

            text = createMessage(repository_name, gh_event, json.dumps(payload))
            text, file_urls = extract_and_clean_urls(text)

            for mapping in topics:
                chat_id, topic_id = mapping.split(':') if ':' in mapping else (mapping, None)
                sendMessage(text, file_urls[0] if file_urls else None, chat_id, topic_id)

if __name__ == "__main__":
    test_rendering()
