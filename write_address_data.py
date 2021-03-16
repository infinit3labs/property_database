from connect_db import get_db_connection
import logging


def get_existing_address_data(data):
    # Get the maximum property_id of the matched address
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""SELECT *
                        FROM (
                        SELECT id,
                               unit_num,
                               street_num,
                               street_name,
                               street_type,
                               suburb,
                               state,
                               postcode,
                               row_number() OVER (ORDER BY id DESC) row_num
                        FROM property_listings.dbo.properties
                        WHERE unit_num = ?
                              AND street_num = ?
                              AND street_name = ?
                              AND street_type = ?
                              AND suburb = ?
                              AND state = ?
                              AND postcode = ?
                        GROUP BY id,
                                 unit_num,
                                 street_num,
                                 street_name,
                                 street_type,
                                 suburb,
                                 state,
                                 postcode
                                 ) t
                        WHERE row_num = 1""",
                       data['address_unit_num'],
                       data['address_street_num'],
                       data['address_street_name'],
                       data['address_street_type'],
                       data['address_suburb'],
                       data['address_state'],
                       data['address_postcode']
                       )
        row = cursor.fetchone()
        cursor.close()
        cnxn.close()
        if row:
            return row[0]
        else:
            return None
    except Exception as e:
        cursor.close()
        cnxn.close()
        logging.warning('Database write failed for: {}: {}'.format(data, e))
        pass


def get_new_property_id(data, pid, sid):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""
        insert into property_listings.dbo.properties (
            property_id,
            source_id,
            unit_num,
            street_num,
            street_name,
            street_type,
            suburb,
            state,
            postcode)
        values (
            ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       pid,
                       sid,
                       data['address_unit_num'],
                       data['address_street_num'],
                       data['address_street_name'],
                       data['address_street_type'],
                       data['address_suburb'],
                       data['address_state'],
                       data['address_postcode']
                       )
        cursor.commit()
        cursor.close()
        cnxn.close()
    except KeyError:
        logging.warning('Could not write to db: {}'.format(data))
        cursor.close()
        cnxn.close()
        pass

    try:
        new_id = get_existing_address_data(data)
        return new_id
    except KeyError:
        logging.warning('Could not retrieve record: {}'.format(data))
        cursor.close()
        cnxn.close()
        pass
