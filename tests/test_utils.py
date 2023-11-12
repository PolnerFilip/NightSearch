import unittest
from unittest.mock import patch

from utils import resolve_contact_page_url, find_contact_page_url


class TestUtils(unittest.TestCase):
    def test_resolve_contact_page_url(self):
        self.assertEquals(resolve_contact_page_url(
            'https://www.harpersbazaar.com/uk/beauty/spas-salons/g22469/best-hair-salons/',
            '/uk/about/a36350/contact-us/'
        ), 'https://www.harpersbazaar.com/uk/about/a36350/contact-us/')
        self.assertEquals(resolve_contact_page_url(
            'https://www.elle.com/uk/beauty/hair/g38672586/best-london-hair-salon/',
            '/uk/about/articles/a30830/contact-us-elle-uk/'
        ), 'https://www.elle.com/uk/about/articles/a30830/contact-us-elle-uk/')
        self.assertEquals(resolve_contact_page_url(
            'https://www.timeout.com/london/shopping/londons-best-hairdressers',
            'https://www.timeout.com/about/contact-us'
        ), 'https://www.timeout.com/about/contact-us')

    @patch('utils.resolve_contact_page_url')
    def test_find_contact_page_url_with_contact_href(self, mock_resolve_contact_page_url):
        base_url = 'http://example.com'
        html = '<html><a href="/contact-us">Contact</a></html>'

        mock_resolve_contact_page_url.return_value = 'http://example.com/contact'

        result = find_contact_page_url(base_url, html)

        self.assertEqual(result, 'http://example.com/contact')
        mock_resolve_contact_page_url.assert_called_with(base_url, '/contact-us')

    @patch('utils.resolve_contact_page_url')
    def test_find_contact_page_url_without_contact_href(self, mock_resolve_contact_page_url):
        base_url = 'http://example.com'
        html = '<html><a href="/about-us">About</a></html>'

        result = find_contact_page_url(base_url, html)

        self.assertIsNone(result)
        mock_resolve_contact_page_url.assert_not_called()


if __name__ == '__main__':
    unittest.main()
