import logging
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import HTTPError
from allhomes_search_builder import get_search_page_url


def total_results():
    # Gets the total results count of the search
    try:
        url = get_search_page_url()
        f = urllib.request.urlopen(url)
        page_data = f.read()
        html_doc = page_data
        soup = BeautifulSoup(html_doc, 'html.parser')

        properties_found = soup.find_all('span', 'css-in3yi3')[0].text.split(' ')[0]
        return properties_found
    except HTTPError:
        logging.error('Cannot retrieve search listings.')
        return None


def get_search_page_data(page_num):
    # Get the results on each search page
    url = get_search_page_url(page_num)
    try:
        f = urllib.request.urlopen(url)
        page_data = f.read()
        html_doc = page_data
        soup = BeautifulSoup(html_doc, 'html.parser')

        results = soup.find_all('div', 'css-1r6lu77')

        return results
    except HTTPError:
        logging.error('Cannot retrieve search page listing: {}'.format(url))
        return None


def get_non_new_home_urls():
    # Filter out the 'new home' listings in the search page results
    # Return the cleaned list of urls
    properties_found = total_results()
    search_pages = int(int(properties_found) / 50) + 2

    property_list = []
    results_not_newhome = []

    try:
        for i in range(1, search_pages):
            all_results = get_search_page_data(i)

            for result in all_results:

                # This checks if the property is 'New Home' and excludes from final list
                if len(result.find_all('span', 'css-1or6om')) > 0:
                    pass
                else:
                    results_not_newhome.append(result)

        for match in results_not_newhome:
            url = match.find_all('a', 'css-11fax8p')[0].attrs['href']
            property_list.append(url)

        return property_list

    except HTTPError:
        logging.error('Cannot retrieve filtered list of urls.')
        return None
