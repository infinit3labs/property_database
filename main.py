from get_search_results import get_non_new_home_urls
from get_re_search_results import re_total_results
from process_allhomes_data import *
from send_email import *
import tests


def main(test, source=None):
    logging.basicConfig(filename='../property_db.log',
                        level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    logging.info('Start.')

    if test and source == 1:
        logging.info('Allhomes TEST')
        results = get_non_new_home_urls()
        for result_url in results:
            process_allhomes_data(result_url)

    elif source == 1:
        results = get_non_new_home_urls()
        logging.info('Allhomes Results: {}'.format(len(results)))
        for result_url in results:
            process_allhomes_data(result_url)

    elif source == 6:
        re_total_results()

    # Send out email with latest listings of the day (if any)
    latest_listings = get_email_data(date.today())
    if latest_listings:
        email_table = format_email_data(latest_listings)
        html = email_table
        send_message('This is an email with property links.', html)
    else:
        logging.info('No new listings today')

    logging.info('End.')


main(test=tests.url, source=6)
