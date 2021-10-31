from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


def simple_get(url):
    """
    Attempts to get the content at a url by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                log_error(f"Error: bad response at {url}")
                return None

    except RequestException as e:
        log_error(f"Error during requests to {url} : {str(e)}")
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers["Content-Type"].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find("html") > -1)


def log_error(e):
    """
    Logs an error to the console.
    """
    print(e)


def get_html(url):
    """
    Parses a response into a BS4 tree, raising exceptions 
    as they come up.
    """
    response = simple_get(url)
    if response is not None:
        html = BeautifulSoup(response, "html.parser")
        return html
    else:
        raise Exception(f"Error retrieving contents at {url}")
