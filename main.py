from datetime import date

from get_search_results import get_non_new_home_urls
from process_allhomes_data import *
from send_email import *
from get_missing_past_sales import *
from write_past_sales_info import *
import tests


def main(test, source=None):
    logging.basicConfig(filename='../property_db.log',
                        level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    logging.info('Start.')

    if test and source == 1:
        logging.info('Allhomes TEST')
        results = [test]
        for result_url in results:
            process_allhomes_data(result_url)

    elif source == 1:
        results = get_non_new_home_urls()
        logging.info('Allhomes Results: {}'.format(len(results)))
        for result_url in results:
            process_allhomes_data(result_url)

    # Run through all properties and check that all past sales recorded
    logging.info('Check for missing past sales')
    urls_pids = get_urls_pids()
    # Loop through properties and get all past sales store details in dictionary
    for pid, url in urls_pids:
        existing_past_sales = get_existing_past_sales(pid)
        soup = get_allhomes_listing_data(url)
        listing_past_sales = get_past_sales_data(soup)
        if existing_past_sales:
            existing_contract_dates = [
                row[2] for row in existing_past_sales
            ]
        else:
            existing_contract_dates = 1
        listing_contract_dates = [
            (idx, sale['contract_date'].date()) for idx, sale in enumerate(listing_past_sales)
        ]
        to_update = []
        to_write = []
        if existing_contract_dates == 1:
            to_write = listing_past_sales
        else:
            for i in listing_contract_dates:
                if i[1] in existing_contract_dates:
                    pass
                else:
                    to_update.append(i)

            for i in to_update:
                to_write.append(listing_past_sales[i[0]])
        if to_write:
            for i in to_write:
                past_sales_write_to_db(pid, 1, i)
        else:
            pass
    logging.info('Complete - check for missing past sales')

    # Send out email with latest listings of the day (if any)
    latest_listings = get_email_data(date.today())
    if latest_listings:
        email_table = format_email_data(latest_listings)
        html = email_table
        send_message('This is an email with property links.', html)
    else:
        logging.info('No new listings today')

    logging.info('End.')


main(test=tests.url, source=1)
