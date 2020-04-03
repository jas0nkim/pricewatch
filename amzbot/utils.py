import re, urllib, io

from PIL import Image
from . import settings


def is_valid_amazon_item_url(url):
    return re.match(settings.AMAZON_COM_ITEM_LINK_PATTERN, url)

def extract_asin_from_url(url):
    match = is_valid_amazon_item_url(url)
    if match:
        return match.group(3)
    else:
        return None

def money_to_float(string):
    # trim everything except number and dot(.)
    return float(re.sub(r'[^\d.]+', '', string))

def extract_int(string):
    # trim everything except number
    return int(re.sub(r'[^\d]+', '', string))

def trim_emojis(string):
    if isinstance(string, str):
        return string.encode('ascii', errors='ignore')
    return string

def replace_html_anchors_to_spans(html):
    # /(<a[^>]*>)([^<]+)(</a>)/
    return re.sub(r'(<a[^>]*>)([^<]+)(</a>)', lambda m: u'<span class="link-replacement">' + m.group(2) + u'</span>', html)

def extract_seller_id_from_uri(uri):
    match = re.match(r'^.+?(?=seller=)([^&]+).*$', uri)
    if match:
        return match.group(1).replace('seller=', '').strip()
    else:
        return None

def get_response_from_url(url):
    """ return http.client.HTTPResponse object
    """
    ret = None
    try:
        response = urllib.request.urlopen(url)
        if response.status != 200:
            raise Exception("HTTP Status is not OK - Status {}".format(response.status))
        ret = response
    except urllib.error.HTTPError as e:
        raise Exception("HTTPError - {}".format(str(e)))
    except urllib.error.URLError as e:
        raise Exception("URLError - {}".format(str(e)))
    return ret

def validate_image_size(url):
    try:
        response = get_response_from_url(url)
        img = Image.open(io.StringIO(response.read()))
    except OSError as e:
        raise Exception("OSError - {}".format(str(e)))
    except ValueError as e:
        raise Exception("ValueError - {}".format(str(e)))
    (width, height) = img.size
    if width < 500 and height < 500:
        raise Exception("Image width and height are less then 500px")
    return True