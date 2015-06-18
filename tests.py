
from unittest import TestCase
from mock import patch, MagicMock
from public_dropbox_urls import DropBoxResource


def returner(*args, **kwargs):
    response_object = MagicMock(*args, **kwargs)
    return response_object


class DropBoxResourceTestCase(TestCase):
    
    def test_resource_init(self):
        document_url = 'https://www.dropbox.com/s/xxxxxxxxxxx/My%20document.docx?dl=1'
        resource = DropBoxResource(document_url)
        self.assertEqual(resource.document_url, document_url)
        self.assertIsNone(resource.is_public)

    @patch('public_dropbox_urls.requests.get')
    def test_resource_init_from_share_url(self, mock_http_get):
        share_url = 'https://www.dropbox.com/l/xxxxxxxxxxxxxxxxxxxxx'
        expected_document_url = 'https://www.dropbox.com/s/xxxxxx/document.docx?dl=1'
        mock_http_get.return_value = returner(
            status_code=302,
            headers={'location': expected_document_url}
        )
        resource = DropBoxResource.from_share_url(share_url)
        self.assertEqual(resource.document_url, expected_document_url)
        self.assertIsNone(resource.is_public)

    @patch('public_dropbox_urls.requests.get')
    def test_resource_resolve_document_url(self, mock_http_get):
        expected_download_url = 'https://dl.dropboxusercontent.com/content_link/xxxxxxxxx?dl=1'
        document_url = 'https://www.dropbox.com/s/xxxxxx/document.docx?dl=1'
        mock_http_get.return_value = returner(
            status_code=302,
            headers={'location': expected_download_url}
        )
        resource = DropBoxResource(document_url)
        resource.resolve()
        self.assertEqual(expected_download_url, resource.download_url)
        self.assertIs(resource.is_public, True)

    @patch('public_dropbox_urls.requests.get')
    def test_resource_resolve_document_url_with_password_protection(self, mock_http_get):
        expected_location = 'sm/password?content_id=xxxxx&cont=https%3A%2F%2Fwww.dropbox.com%2Fs%2Fxxxxx%3Fdl%3D1'
        document_url = 'https://www.dropbox.com/s/xxxxxx/document.docx?dl=1'
        mock_http_get.return_value = returner(
            status_code=302,
            headers={'location': expected_location}
        )
        resource = DropBoxResource(document_url)
        resource.resolve()
        self.assertIs(resource.is_public, False)
        self.assertIsNone(resource.download_url)

    @patch('public_dropbox_urls.requests.get')
    def test_resource_resolve_expired_document_url(self, mock_http_get):
        document_url = 'https://www.dropbox.com/s/xxxxxx/document.docx?dl=1'
        mock_http_get.return_value = returner(
            status_code=200,
            content='<html><title>Link expired - Dropbox</title> blah blah blah...',
            headers={}
        )
        resource = DropBoxResource(document_url)
        resource.resolve()
        self.assertIs(resource.is_public, False)
        self.assertIsNone(resource.download_url)
