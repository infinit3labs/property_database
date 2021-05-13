from sendgrid import SendGridAPIClient
import logging
from connect_db import *
from config import *


def get_email_data(date):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""EXEC get_latest_listings ?""",
                       date
                       )
        rows = cursor.fetchall()
        cursor.close()
        cnxn.close()
        if rows:
            return rows
        else:
            return None
    except Exception as e:
        cursor.close()
        cnxn.close()
        logging.warning('Failed to get latest listings: {}'.format(e))
        pass


def format_email_data(data):
    import fnmatch
    import pandas as pd

    price = [(item[0], item[2]) for item in data if item[1] == 'price']
    bedrooms = [(item[0], item[2]) for item in data if item[1] == 'bedrooms']
    living_size = []
    for item in data:
        try:
            if fnmatch.fnmatch(item[1], '*size') and int(item[2].split(' m²')[0]) <= 400:
                living_size.append((item[0], item[2].split(' m²')[0]))
        except ValueError:
            living_size.append((item[0], ''))
    suburb = [(item[0], item[2]) for item in data if item[1] == 'suburb']
    prop_type = [(item[0], item[2].lower()) for item in data if item[1] == 'property type']
    courtyard = [(item[0], item[2]) for item in data if item[1] == 'has_courtyard']
    url = [(item[0], item[2]) for item in data if item[1] == 'url']
    pids = [item[0] for item in url]

    # Create dataframe; populate with data
    cols = ['price', 'bedrooms', 'living_size', 'suburb', 'prop_type', 'courtyard', 'url']
    idx = pids

    df = pd.DataFrame(index=idx,
                      columns=cols)

    for p in price:
        df.loc[p[0], 'price'] = p[1]
    for p in bedrooms:
        df.loc[p[0], 'bedrooms'] = p[1]
    for p in living_size:
        df.loc[p[0], 'living_size'] = p[1]
    for p in suburb:
        df.loc[p[0], 'suburb'] = p[1]
    for p in prop_type:
        df.loc[p[0], 'prop_type'] = p[1]
    for p in courtyard:
        df.loc[p[0], 'courtyard'] = p[1]
    for p in url:
        df.loc[p[0], 'url'] = p[1]

    df_html = df.to_html()

    return df_html


def build_message(text, html):
    from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent, SendGridException

    message = Mail(
        from_email=From(FROM_EMAIL, FROM_NAME),
        to_emails=[
            To(TO_EMAILS[0], TO_NAMES[0]),
            To(TO_EMAILS[1], TO_NAMES[1])
            ],
        subject=Subject("Today's Property Listings"),
        plain_text_content=PlainTextContent(text),
        html_content=HtmlContent(html)
    )

    return message

    # try:
    #     print(json.dumps(message.get(), sort_keys=True, indent=4))
    #     return message.get()
    #
    # except SendGridException as e:
    #     print(e, message)


def send_message(text, html):
    message = build_message(text, html)
    sendgrid_client = SendGridAPIClient(api_key=SENDGRID_KEY)
    response = sendgrid_client.send(message=message)
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)


# TESTS

# text = 'and easy to do anywhere, even with Python'
# test = get_email_data('2021-05-13')
# if test:
#     email_table = format_email_data(test)
#     html = email_table
#     send_message(text, html)
# print(test)

