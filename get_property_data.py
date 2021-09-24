import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import logging
import re


def get_allhomes_listing_data(url):
    """
    """
    listing_url = url
    try:
        f = urllib.request.urlopen(url)
        page_data = f.read()
        html_doc = page_data
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup
    except HTTPError as e:
        print('Query failed: {}: {}'.format(url, e))
        return None


def get_price(soup):
    try:
        price_raw = soup.find_all('div', 'css-5xe854')[0].text
        # price_nums = []
        # for p in price_raw:
        #     if p.isdigit():
        #         price_nums.append(p)
        # price_val = ''.join(map(str, price_nums))
        price = {'price': price_raw}
        return price
    except IndexError as e:
        logging.warning('No price data available: {}'.format(e))
        return None


def get_listing_icon_data(soup):
    # Extract main listing data at top of page
    listing_details = soup.find_all('span', 'css-8dprsf')

    listing_details_data = {}

    if listing_details:
        for i in listing_details:
            try:
                _val = i.find_all('span')[0].text
                _type = i.find_all('svg')[0].text
                listing_details_data[_type] = _val
            except IndexError as e:
                logging.warning('Capture of icon data failed: {}'.format(e))

    if 'EER' in listing_details_data.keys():
        del listing_details_data['EER']

    return listing_details_data


def get_key_details_data(soup):
    # Extract data from the Key Details section of the page
    key_details_data = {}

    key_details = soup.find_all('div', 'css-hboir5')

    if key_details:
        for detail in key_details:
            try:
                _key = detail.find_all('span', 'css-nqo9lc')[0].text.split(':')[0]
            except IndexError:
                try:
                    _key = detail.find_all('span', 'css-nqo9lc')[0].text
                except IndexError:
                    _key = 'N/A'
            try:
                _val = detail.find_all('span', 'css-5hg4fg')[0].text
            except IndexError:
                _val = 'N/A'
            key_details_data[_key] = _val

    return key_details_data


def get_current_listing_data(soup):
    # Current Sales Info
    # views, list date, update date, property id

    current_sales_data = {}
    try:
        listing_info = soup.find_all('div', 'css-mqbtts')[0].text
        current_sales_data['property_id'] = int(listing_info.split(': ')[1][:9])
        max_views_loc = listing_info.find('times') - 1
        min_views_loc = listing_info.find('viewed') + 7
        current_sales_data['views'] = listing_info[min_views_loc:max_views_loc]
        list_date_loc = listing_info.find('displayed')
        current_sales_data['list_date'] = datetime.strptime(
            listing_info[list_date_loc + 13:list_date_loc + 23], '%d/%m/%Y'
        )
        update_date_loc = listing_info.find('updated')
        current_sales_data['update_date'] = datetime.strptime(
            listing_info[update_date_loc + 11:update_date_loc + 21], '%d/%m/%Y'
        )
    except IndexError as e:
        logging.warning('Property probably off the market now: {}'.format(e))
        return None

    return current_sales_data


def get_land_values(key_details_data):
    # Land Values
    # Unimproved value, unimproved year

    land_values_data = {}
    try:
        uv_raw = key_details_data['Unimproved Value'].split(' ')[0]
        uv_nums = []
        for u in uv_raw:
            if u.isdigit():
                uv_nums.append(u)
        land_values_data['uv'] = ''.join(map(str, uv_nums))
    except KeyError:
        land_values_data['uv'] = None
    try:
        land_values_data['uv_year'] = key_details_data['Unimproved Value'].split(' ')[1].split('(')[1].split(')')[0]
    except KeyError:
        land_values_data['uv_year'] = None

    if land_values_data['uv'] and land_values_data['uv_year']:
        return land_values_data
    else:
        logging.warning('Could not capture any land value data')
        return None


def get_past_sales_data(soup):
    # Past Sales Data
    # price, list date, contract date, transfer date, days on market

    prev_sales_data = []

    prev_sales = soup.find_all('div', 'css-1waaw1k')

    if prev_sales:
        for i in prev_sales:
            sale_type = i.find_all('div', 'css-13it8mc')[0].text
            price_str = i.find_all('div', 'css-wtlu8o')[0].text
            price_nums = []
            for ii in price_str:
                if ii.isdigit():
                    price_nums.append(ii)
            price = ''.join(price_nums)
            details = i.find_all('div', 'css-104pj7g')

            prev_sale_details_data = {}

            if details:
                for detail in details:
                    _key = detail.text.split(': ')[0]
                    _val = detail.text.split(': ')[1]
                    prev_sale_details_data[_key] = _val

            try:
                contract_str = prev_sale_details_data['Contract']
                contract_dt = datetime.strptime(contract_str, '%d/%m/%Y')
            except KeyError:
                contract_dt = date(9999, 1, 1)
            try:
                tfer_str = prev_sale_details_data['Transfer']
                tfer_dt = datetime.strptime(tfer_str, '%d/%m/%Y')
            except KeyError:
                tfer_dt = date(9999, 1, 1)
            try:
                listed_str = prev_sale_details_data['Listed']
                listed_dt = datetime.strptime(listed_str, '%d/%m/%Y')
            except KeyError:
                listed_dt = date(9999, 1, 1)

            prev_sales_data.append({
                'sale_type': sale_type,
                'price': price,
                'contract_date': contract_dt,
                'transfer_date': tfer_dt,
                'listed_date': listed_dt
            })

    return prev_sales_data


def get_address_data(soup, url):
    # Deal with various formats of an address
    # This could be improved but handles > 90% of cases
    # TODO: Probably don't need the url at all
    url_str_list = url.split('/')[-1].split('-')
    str_list_ex_pcode = url_str_list[:-1]
    breadcrumbs = soup.find_all('a', 'css-1tiqujk')
    breadcrumb_list = []
    for item in breadcrumbs:
        breadcrumb_list.append(item.text)
    str_nums = []
    str_nums_idx = []
    for idx, item in enumerate(str_list_ex_pcode):
        try:
            int(item)
            str_nums_idx.append(idx)
            str_nums.append(item)
        except ValueError:
            try:
                # TODO: Deal with letter in front of street or unit number
                r = re.match('[0-9]+[a-zA-Z]{1}', item)
                if r:
                    str_nums_idx.append(idx)
                    str_nums.append(item)
            except ValueError:
                pass
    try:
        street_str = soup.find_all('h1', 'css-hed0vw')[0].text
    except IndexError as e:
        # Likely off the market
        logging.warning('Could not get street info: {}'.format(e))
        return None
    street_details = street_str.split(',')[0]
    street_details_list = street_details.split(' ')
    if street_details_list[0].lower() == 'unit':
        street_details_nums = street_details_list[1]
    else:
        street_details_nums = street_details_list[0]
    if street_details_nums.find('/') >= 0:
        str_details_nums_1 = [street_details_nums.split('/')[0]]
        str_details_nums_2 = street_details_nums.split('/')[1].split('-')
        str_details_nums_list = str_details_nums_1 + str_details_nums_2
        str_details_clean = str_details_nums_list + street_details_list[1:]
    else:
        str_details_clean = street_details_list
        str_details_nums_list = str_nums
    str_details_nums_idx = []
    for idx, item in enumerate(str_details_clean):
        try:
            int(item)
            str_details_nums_idx.append(idx)
        except ValueError:
            try:
                # TODO: Deal with letter in front of street or unit number
                r = re.match('[0-9]+[a-zA-Z]{1}', item)
                if r:
                    str_details_nums_idx.append(idx)
            except ValueError:
                pass

    street_postcode = street_str.split(',')[1].split(' ')[-1]
    street_state = url_str_list[-2]
    street_type = street_details_list[-1]
    street_suburb = breadcrumb_list[-1]
    address_unit_num = 'N/A'
    address_street_num = 'N/A'

    # Scenario 8: deal with no address details
    if street_details_nums == '(no':
        logging.warning('No street details provided: {}'.format(url))
        return None

    # Scenario 9: unhandled format of address
    if len(str_details_nums_idx) == 0 or len(str_nums_idx) == 0:
        logging.warning('Cannot parse address: {}'.format(url))
        return None

    # Scenario 1: single street number: count of str details num list = 1
    if len(str_details_nums_list) == 1:
        address_street_num = str_details_clean[0]

    # Scenario 2: hyphenated street number: count of str details num list = 3
    if len(str_details_nums_list) == 3:
        address_unit_num = str_details_nums_list[0]
        address_street_num = '-'.join(str_details_nums_list[1:])

    # Scenario 3: multiple street names
    street_details_list_len = len(str_details_clean)
    max_str_name_idx = street_details_list_len - 1
    max_str_num_idx = str_details_nums_idx[-1]
    str_name_count = max_str_name_idx - (max_str_num_idx + 1)
    i = max_str_num_idx + 1
    str_names = []
    while i < max_str_name_idx:
        str_names.append(str_details_clean[i])
        i += 1
    address_street_name = ' '.join(str_names)

    # Scenario 4: deal with unit number
    if len(str_details_nums_list) == 2:
        address_unit_num = str_details_nums_list[0]
        address_street_num = str_details_nums_list[1]

    property_address_data = {
        'address_unit_num': address_unit_num[:5],
        'address_street_num': address_street_num[:5],
        'address_street_name': address_street_name[:50],
        'address_street_type': street_type[:50],
        'address_suburb': street_suburb[:50],
        'address_state': street_state[:10],
        'address_postcode': street_postcode[:5]
    }

    return property_address_data


def get_listing_dates(soup):
    # At the moment get next inspection date and the auction date if applicable

    listing_dates_data = {}

    # The auction date is in the price field
    price = soup.find_all('div', 'css-5xe854')[0].text
    try:
        if price[:7].lower() == 'auction' and len(price.split(' ')[1]) == 8:
            auction_date_str = price.split(' ')[1]
            auction_dt = datetime.strptime(auction_date_str, '%d/%m/%y')
            listing_dates_data['auction_dt'] = auction_dt
        else:
            logging.warning('Could be issue with auction details on listing.')
            pass
    except Exception as e:
        logging.warning('Could be issue with auction details on listing: {}'.format(e))

    try:
        # This is taken from the RHS sidebar where the agent details are
        next_inspection_str = soup.find_all('div', 'css-1wul2ro')[0]
        next_inspection_str = soup.find_all('div', 'css-1vabjgz')[0].find_all('span')[0].attrs['content']
        listing_dates_data['next_inspection_dt'] = datetime.strptime(
            next_inspection_str, '%Y-%m-%dT%H:%M:%S'
        )
    except IndexError as e:
        logging.warning('No next inspection date available: {}'.format(e))
        pass

    return listing_dates_data


def get_property_flags(soup):
    # To track points of interest about the property.
    # This can track time taken from listing to receive an accepted offer or sell

    property_flags = {}

    try:
        if soup.find_all('span', 'css-noxayc')[0].text == 'Offer':
            property_flags['has_offer'] = 'Y'
    except IndexError as e:
        logging.info('Either no offer flag or css has failed; setting to N: {}'.format(e))
        property_flags['has_offer'] = 'N'

    try:
        if soup.find_all('span', 'css-14zapsz')[0].text == 'Sold':
            property_flags['is_sold'] = 'Y'
    except IndexError as e:
        logging.info('Either no sale flag or css has failed; setting to N: {}'.format(e))
        property_flags['is_sold'] = 'N'

    try:
        has_courtyard = soup.find_all('div', 'css-1josczm')[0].text.lower().find('courtyard')
        if has_courtyard >= 0:
            property_flags['has_courtyard'] = 'Y'
        else:
            property_flags['has_courtyard'] = 'N'
    except IndexError:
        property_flags['has_courtyard'] = 'N'

    return property_flags
