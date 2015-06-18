
## 0.0.0.1

* First pass at DropboxResource

## 0.0.0.2

* Rethink the criteria for saying a link is expired

## 0.0.0.3 

* Add 'DropBoxResource.from_redirect_url' method to allow getting a download_url from the exact 
  url provided by dropbox if you click share and then use the available url manually
* Breaking change DropBoxResource.document_url to redirect_url.
* Drop share_url keyword argument in __init__ constructor.

## 0.0.0.4

* Add REDIRECT_URL_PATTERN and SHARE_URL constants for reference.
* Revert DropBoxResource.redirect_url to be document_url.
* Get tests working again.

