from connect_db import get_db_connection
import logging


def lv_check_in_db(pid, sid):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    try:
        row = cursor.execute("""
            select *
            from (
            select id,
                   row_number() OVER (order by id desc) row_num
            from land_values
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


def lv_details_changed(id, data):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    row = None
    try:
        row = cursor.execute("""
            select property_id,
            source_id,
            value,
            year
            from land_values
            where id = ?
        """, id)
        row = cursor.fetchone()
    except Exception as e:
        logging.warning('Could not query db: {}, {}: {}'.format(id,
                                                                data,
                                                                e))
        cursor.close()
        cnxn.close()

    _new_uv = int(data['uv'])
    _new_uv_year = int(data['uv_year'])

    _old_uv = row[2]
    _old_uv_year = row[3]

    if _old_uv != _new_uv or _old_uv_year != _new_uv_year:
        cursor.execute("""
            update land_values
            set details_end_date = getdate()
            where id = ?
        """, id)
        cursor.commit()
        cursor.close()
        cnxn.close()
        lv_write_to_db(row[0], row[1], data)


def lv_write_to_db(pid, sid, data):
    _property_id = int(pid)
    _source_id = int(sid)
    _land_data = data

    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""
            INSERT INTO land_values (
                property_id,
                source_id,
                value,
                year)
            VALUES (
                ?, ?, ?, ?)""",
                       pid,
                       sid,
                       data['uv'],
                       data['uv_year']
                       )
        cursor.commit()
        cursor.close()
        cnxn.close()
    except Exception as e:
        logging.warning('Could not query db: {}, {}, {}: {}'.format(pid,
                                                                    sid,
                                                                    data,
                                                                    e))
        cursor.close()
        cnxn.close()
        pass


