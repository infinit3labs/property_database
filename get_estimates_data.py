import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import logging


def get_estimates_data(url, address=None):
    if url:
        property_slug_raw = url.split('/')[3]
        if property_slug_raw.find('?') >= 0:
            property_slug_raw = property_slug_raw.split('?')[0]
        if property_slug_raw.find('unit-') >= 0:
            property_slug_clean = property_slug_raw.split('unit-')[1]
        else:
            property_slug_clean = property_slug_raw
        estimate_base_url = 'https://www.domain.com.au/property-profile/'
        estimate_url = estimate_base_url + property_slug_clean
        try:
            f = urllib.request.urlopen(estimate_url)
            page_data = f.read()
            html_doc = page_data
            soup = BeautifulSoup(html_doc, 'html.parser')

            data = {}
            try:
                confidence_level_str = soup.find_all('div', 'css-2bfnfy')[0].text
                confidence_level_type = None
                if confidence_level_str.lower().find('high') >= 0:
                    confidence_level_type = 'high'
                if confidence_level_str.lower().find('medium') >= 0:
                    confidence_level_type = 'medium'
                if confidence_level_str.lower().find('low') >= 0:
                    confidence_level_type = 'low'
                if confidence_level_type:
                    data['confidence_level'] = confidence_level_type
            except IndexError:
                pass

            price_range = soup.find_all('div', 'css-2i8bfi')
            if len(price_range) == 3:
                data['low_estimate'] = price_range[0].text.split('$')[1]
                data['mid_estimate'] = price_range[1].text.split('$')[1]
                data['high_estimate'] = price_range[2].text.split('$')[1]
                return data
            else:
                logging.warning('No estimate data available: {}'.format(estimate_url))
                return None
        except HTTPError:
            logging.warning('Request to estimate site failed: {}'.format(estimate_url))
            return None
