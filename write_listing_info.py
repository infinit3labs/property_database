from connect_db import get_db_connection
import logging


def list_check_in_db(pid, sid):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    try:
        row = cursor.execute("""
            select *
            from (
            select id,
                   row_number() OVER (order by id desc) row_num
            from listings
            where property_id = ?
            and source_id = ?) t 
            where row_num = 1
        """, pid, sid)
        row = cursor.fetchone()
        cursor.close()
        cnxn.close()
        if row:
            return row[0]
        else:
            return None
    except Exception as e:
        logging.warning('Could not query db: {}, {}: {}'.format(pid,
                                                                sid,
                                                                e))
        cursor.close()
        cnxn.close()


def list_details_changed(id, url, data):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    row = None
    try:
        row = cursor.execute("""
            select property_id,
            source_id,
            views,
            list_date,
            update_date,
            url
            from listings
            where id = ?
        """, id)
        row = cursor.fetchone()
    except Exception as e:
        logging.warning('Could not query db: {}, {}, {}: {}'.format(id,
                                                                    url,
                                                                    data,
                                                                    e))
        cursor.close()
        cnxn.close()

    _new_views = int(data['views'])
    _new_list_date = data['list_date'].date()
    _new_update_date = data['update_date'].date()
    _new_url = url

    _old_views = row[2]
    _old_list_date = row[3]
    _old_update_date = row[4]
    _old_url = row[5]

    if _old_views != _new_views or \
            _old_list_date != _new_list_date or \
            _old_update_date != _new_update_date or \
            _old_url != _new_url:
        cursor.execute("""
            update listings
            set details_end_date = getdate()
            where id = ?
        """, id)
        cursor.commit()
        cursor.close()
        cnxn.close()
        list_write_to_db(row[0], row[1], url, data)


def list_write_to_db(pid, sid, url, data):
    _property_id = int(pid)
    _source_id = int(sid)
    _listing_data = data

    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""
            INSERT INTO listings (
                property_id,
                source_id,
                views,
                list_date,
                update_date,
                url)
            VALUES (
                ?, ?, ?, ?, ?, ?)""",
                       pid,
                       sid,
                       data['views'],
                       data['list_date'],
                       data['update_date'],
                       url
                       )
        cursor.commit()
        cursor.close()
        cnxn.close()
    except Exception as e:
        logging.warning('Could not query db: {}, {}, {}, {}: {}'.format(pid,
                                                                        sid,
                                                                        url,
                                                                        data,
                                                                        e))
        cursor.close()
        cnxn.close()
        pass
