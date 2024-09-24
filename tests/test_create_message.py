import unittest
import json
import logging
from main_local import createMessage

class TestCreateMessage(unittest.TestCase):

    def load_json_payload(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def load_expected_message(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def test_create_message_issue_comment_event(self):
        repository_name = "Test-repo"
        gh_event = "issue_comment"
        body = json.dumps(self.load_json_payload('./tests/payloads/issue_comment/issue_comment_test_1.json'))
        expected_message = self.load_expected_message('./tests/expected_messages/issue_comment_expected_1.txt').strip()
        message = createMessage(repository_name, gh_event, body).strip()
        self.assertEqual(message, expected_message)

    def test_create_message_issues_event(self):
        repository_name = "Test-repo"
        gh_event = "issues"
        body = json.dumps(self.load_json_payload('./tests/payloads/issues/issues_test_1.json'))
        expected_message = self.load_expected_message('./tests/expected_messages/issues_expected_1.txt').strip()
        message = createMessage(repository_name, gh_event, body).strip()
        self.assertEqual(message, expected_message)

    def test_create_message_template_not_found(self):
        repository_name = "Test-repo"
        gh_event = "non_existent_event"
        body = json.dumps({
            "some_key": "some_value"
        })
        expected_message = ""
        message = createMessage(repository_name, gh_event, body)
        self.assertEqual(message, expected_message)

    def test_create_message_invalid_json(self):
        repository_name = "Test-repo"
        gh_event = "issue_push"
        body = "{invalid_json}"
        expected_message = ""
        message = createMessage(repository_name, gh_event, body)
        self.assertEqual(message, expected_message)

if __name__ == '__main__':
    unittest.main()
