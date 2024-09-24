import unittest
from main_local import extract_and_clean_urls

class TestExtractAndCleanUrls(unittest.TestCase):
    
    def test_single_url(self):
        text = "![Image](https://github.com/user/repo/assets/file/1234)\r\nSome text"
        expected_clean_text = "Some text"
        expected_urls = ["https://github.com/user/repo/assets/file/1234"]
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)
        
    def test_multiple_urls(self):
        text = "![Image1](https://github.com/user1/repo1/assets/file1/1234)\r\nSome text ![Image2](https://github.com/user2/repo2/assets/file2/5678)\r\nAnother text"
        expected_clean_text = "Some text [Image2](https://github.com/user2/repo2/assets/file2/5678)\r\nAnother text"
        expected_urls = ["https://github.com/user1/repo1/assets/file1/1234", "https://github.com/user2/repo2/assets/file2/5678"]
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)
        
    def test_no_urls(self):
        text = "Some text without any URLs"
        expected_clean_text = "Some text without any URLs"
        expected_urls = []
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)
        
    def test_non_matching_urls(self):
        text = "![Image](https://example.com/user/repo/assets/file/1234)\r\nSome text"
        expected_clean_text = "[Image](https://example.com/user/repo/assets/file/1234)\r\nSome text"
        expected_urls = []
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)

    def test_mixed_content(self):
        text = "Some intro text ![Image1](https://github.com/user/repo/assets/file1/1234)\r\nMore text ![Image2](https://github.com/user/repo/assets/file2/5678)\r\nConclusion text"
        expected_clean_text = "Some intro text More text [Image2](https://github.com/user/repo/assets/file2/5678)\r\nConclusion text"
        expected_urls = ["https://github.com/user/repo/assets/file1/1234", "https://github.com/user/repo/assets/file2/5678"]
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)

    def test_empty_text(self):
        text = ""
        expected_clean_text = ""
        expected_urls = []
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)

    def test_text_with_line_breaks(self):
        text = "![Image](https://github.com/user/repo/assets/file/1234)\r\nSome text with\r\nmultiple line breaks"
        expected_clean_text = "Some text with\r\nmultiple line breaks"
        expected_urls = ["https://github.com/user/repo/assets/file/1234"]
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)

    def test_only_urls(self):
        text = "![Image1](https://github.com/user/repo/assets/file1/1234)\r\n![Image2](https://github.com/user/repo/assets/file2/5678)\r\n"
        expected_clean_text = "[Image2](https://github.com/user/repo/assets/file2/5678)\r\n"
        expected_urls = ["https://github.com/user/repo/assets/file1/1234", "https://github.com/user/repo/assets/file2/5678"]
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)
        
    def test_malformed_urls(self):
        text = "![Image](https://github.com/user/repo/assets/file1234)\r\nSome text ![Image](https://github.com/user/repo/assets/file/5678)\r\nMore text"
        expected_clean_text = "[Image](https://github.com/user/repo/assets/file1234)\r\nSome text More text"
        expected_urls = ["https://github.com/user/repo/assets/file/5678"]
        clean_text, file_urls = extract_and_clean_urls(text)
        self.assertEqual(clean_text, expected_clean_text)
        self.assertEqual(file_urls, expected_urls)

if __name__ == '__main__':
    unittest.main()
