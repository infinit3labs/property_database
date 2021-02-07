import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import logging
from connect_db import *


def get_prop_val_data(address):

    unit_num = address['address_unit_num']
    street_num = address['address_street_num']
    street_name = address['address_street_name']
    street_type = address['address_street_type']
    suburb = address['address_suburb']
    state = address['address_state'].upper()
    postcode = address['address_postcode']

    address_clean = None

    if unit_num == 'N/A':
        address_clean = f'{street_num} {street_name} {street_type} ' \
                        f'{suburb} {state} {postcode}'
    else:
        address_clean = f'{unit_num}/{street_num} {street_name} {street_type} ' \
                        f'{suburb} {state} {postcode}'

    if address_clean:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # Needed to prevent Chrome crashing using root user
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.propertyvalue.com.au/")
        driver.find_element_by_id('acceptCookieButton').click()

        elem = driver.find_element_by_id('propertysearch')
        elem.clear()
        elem.send_keys(address_clean)
        time.sleep(2)
        elem.send_keys(Keys.RETURN)
        time.sleep(2)

        try:
            driver.find_element_by_id('errorModal')
            driver.find_element_by_class_name('btn-primary').click()
        except Exception:
            logging.info('No Error Modal')
            pass
        time.sleep(2)

        url = driver.current_url
        if 'did-you-mean' in url:
            suggestions = driver.find_element_by_xpath(
                '/html/body/div[1]/table[2]/tbody/tr/td/table/tbody/tr[1]/td/div/div/div[2]/a').click()
            time.sleep(2)

        if address_clean[:2] in driver.title:
            try:
                url = driver.current_url
                price = driver.find_element_by_id('propEstimatedPrice').text
                confidence = driver.find_element_by_class_name('confidence').text
            except NoSuchElementException:
                logging.warning('Page does not contain estimate data.')
                driver.close()
                return None

            driver.close()

            low_price = price.split(' - ')[0]
            high_price = price.split(' - ')[1]

            low_nums = [i for i in low_price if i.isdigit()]
            high_nums = [i for i in high_price if i.isdigit()]

            low_price = ''.join(low_nums)
            high_price = ''.join(high_nums)

            data = {
                'low_estimate': low_price,
                'high_estimate': high_price,
                'confidence_level': confidence.split(' ')[0].lower()
            }

            return data

        else:
            logging.warning('Page did not load correctly.')
            driver.close()
            return None


def check_in_db(pid, sid):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""select *
                            from estimates
                            where property_id = ?
                            and source_id = ?""",
                       pid,
                       sid
                       )
        row = cursor.fetchone()
        cursor.close()
        cnxn.close()
        if row:
            return 1
        else:
            return None
    except Exception as e:
        cursor.close()
        cnxn.close()
        logging.warning('Database query failed for: {}: {}'.format(pid, e))
        pass
