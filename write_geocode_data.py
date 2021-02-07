from connect_db import get_db_connection
import logging


def get_existing_geocode_data(formatted_adr):
    # Get the maximum property_id of the matched address
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""select *
                          from geocodes
                          where name = ?""",
                       formatted_adr
                       )
        row = cursor.fetchone()
        cursor.close()
        cnxn.close()
        if row:
            return {
                'id': row[0],
                'lat': row[4],
                'lon': row[5],
                'name': row[6],
            }
        else:
            return None
    except Exception as e:
        cursor.close()
        cnxn.close()
        logging.warning('Database check failed for: {}: {}'.format(formatted_adr, e))
        pass


def write_new_geocode(sid, data):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""
            INSERT INTO geocodes (
                source_id,
                lat,
                lon,
                name)
            VALUES (
                ?, ?, ?, ?)""",
                       sid,
                       data['lat'],
                       data['lon'],
                       data['name']
                       )
        cursor.commit()
        cursor.close()
        cnxn.close()
    except Exception as e:
        logging.warning('Could not query db: {}, {}: {}'.format(sid,
                                                                data,
                                                                e))
        cursor.close()
        cnxn.close()
        pass


def update_properties(gid, data):
    # Update properties without geocode data
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""UPDATE properties
                            SET geocode_id = ?
                            WHERE street_num = ?
                            AND street_name = ?
                            AND street_type = ?
                            AND suburb = ?
                            AND state = ?
                            AND postcode = ?
                            AND geocode_id is NULL""",
                       gid,
                       data['address_street_num'],
                       data['address_street_name'],
                       data['address_street_type'],
                       data['address_suburb'],
                       data['address_state'],
                       data['address_postcode'],
                       )
        cursor.commit()
        cursor.close()
        cnxn.close()
        cursor = None
        cnxn = None
    except Exception as e:
        cursor.close()
        cnxn.close()
        cursor = None
        cnxn = None
        logging.warning('Database write failed for: {}: {}'.format(data, e))
        return None
