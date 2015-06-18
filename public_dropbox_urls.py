from urlparse import urlparse
import requests


# Share URL pattern is a shortened link that redirects
# to the redirect URL; something like:
# "https://www.dropbox.com/l/xxxxxxxxxxxxxxxxxxxxx"
SHARE_URL_PATTERN = "https://www\.dropbox\.com/l/.+"

# The redirect URL contains some random-seeming characters
# as well as the document title and querystring parameters; something like:
# "https://www.dropbox.com/s/xxxxxxxxxxx/My%20document.docx?dl=0"
REDIRECT_URL_PATTERN = "https://www\.dropbox\.com/s/.+"


class DropBoxResource(object):
    """
    Object responsible for representing a remotely accessible 
    DropBox document. Takes an input_url, which should be the
    URL of the document as it can be accessed when one clicks
    "Share" in their web application, but supplies "dl?=1" as
    a querystring parameter. Something like:
    'https://www.dropbox.com/s/xxxxxxxxxxx/My%20document.docx?dl=1'.

    Alternatively, there is a `from_share_url` method that expects
    a url formatted as described by SHARE_URL_PATTERN.

    Finally, there is `from_redirect_url`, which expects the
    same thing as the regular constructor, except the querystring
    parameters are ignored, and "dl?=1" will be added; see
    REDIRECT_URL_PATTERN for what this should look like.
    """

    def __init__(self, document_url):
        self.document_url = document_url
        self.download_url = None
        self.is_public = None

    @classmethod
    def from_share_url(cls, share_url):
        resp = requests.get(share_url, allow_redirects=False)
        return cls.from_redirect_url(resp.headers.get('location'))

    @classmethod
    def from_redirect_url(cls, redirect_url):
        # The redirect location has querystring parameters
        # that make the page render in a way we don't want;
        # remove them and supply '?dl=1', for downloading.
        parsed_url = urlparse(redirect_url)
        document_url = (
            parsed_url.scheme + '://' +
            parsed_url.netloc +
            parsed_url.path + '?dl=1'
        )
        return cls(document_url)

    def resolve(self):
        resp = requests.get(self.document_url, allow_redirects=False)

        if resp.status_code == 302:
            redirect_location = resp.headers.get('location')
            if self._looks_password_protected(redirect_location):
                self.is_public = False
            else:
                self.download_url = redirect_location
                self.is_public = True

        elif resp.status_code is requests.codes.ok:
            # If we got here, this may signify an expired link
            if self._looks_expired(resp.content):
                self.is_public = False
            else:
                # unknown state
                pass

        else:
            # unknown error
            pass

    @staticmethod
    def _looks_password_protected(url):
        return 'password' in url

    @staticmethod
    def _looks_expired(content):
        return '<title>Link expired - Dropbox</title>' in content

