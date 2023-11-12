import unittest
from unittest.mock import patch, Mock

from bson import ObjectId

from tasks import find_contact_page, find_contact_page_callback


class TestTasks(unittest.TestCase):
    @patch('requests.get')
    @patch('tasks.find_contact_page_url')
    @patch('tasks.insert_to_mongodb')
    def test_find_contact_page(self, mock_insert_to_mongodb, mock_find_contact_page_url, mock_requests_get):
        mock_response = Mock()
        mock_response.text = '<html><a href="/contact-us">Contact</a></html>'
        mock_requests_get.return_value = mock_response

        object_id = ObjectId()
        mock_find_contact_page_url.return_value = 'http://example.com/contact'
        mock_insert_to_mongodb.return_value = object_id

        expected_result = {
            'page_name': 'Example Page',
            'page_url': 'http://example.com',
            'contact_page_url': 'http://example.com/contact'
        }

        page_url = 'http://example.com'
        page_name = 'Example Page'
        keyword = 'example'

        result = find_contact_page(page_url, page_name, keyword)

        self.assertEqual(result, expected_result)
        mock_requests_get.assert_called_with(page_url, timeout=5)
        mock_find_contact_page_url.assert_called_with(page_url, mock_response.text)
        mock_insert_to_mongodb.assert_called_with(page_name, page_url, 'http://example.com/contact', keyword)

    @patch('requests.get')
    def test_find_contact_page_contact_not_found(self, mock_requests_get):
        mock_response = Mock()
        mock_response.text = '<html><a href="/about-us">About Us</a></html>'
        mock_requests_get.return_value = mock_response

        result = find_contact_page('http://example.com', 'Example Page', 'example')
        self.assertEqual(result, False)

    def test_find_contact_page_callback(self):
        dict_placeholder = {'key': 'value'}
        results = [dict_placeholder, dict_placeholder, None, dict_placeholder, None, None, dict_placeholder]
        expected_result = [dict_placeholder, dict_placeholder, dict_placeholder, dict_placeholder]
        result = find_contact_page_callback(results)

        self.assertEqual(len(result), 4)
        self.assertEqual(result, expected_result)



if __name__ == '__main__':
    unittest.main()
