from connect_db import get_db_connection
import logging


def feature_check_in_db(pid, sid, name):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    try:
        row = cursor.execute("""
            select *
            from (
            select id,
                   row_number() OVER (order by id desc) row_num
            from property_features
            where property_id = ?
            and source_id = ?
            and name = ?) t 
            where row_num = 1
        """, pid, sid, name)
        row = cursor.fetchone()
        cursor.close()
        cnxn.close()
        if row:
            return row[0]
        else:
            return None
    except Exception as e:
        logging.warning('Could not query db: {}, {}, {}: {}'.format(pid,
                                                                    sid,
                                                                    name,
                                                                    e))
        cursor.close()
        cnxn.close()


def feature_details_changed(id, name, value):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    row = None
    try:
        row = cursor.execute("""
            select property_id,
            source_id,
            name,
            value
            from property_features
            where id = ?
        """, id)
        row = cursor.fetchone()
    except Exception as e:
        logging.warning('Could not query db: {}, {}, {}: {}'.format(id,
                                                                    name,
                                                                    value,
                                                                    e))

    _new_name = name.lower()
    _new_value = value

    _old_name = row[2]
    _old_value = row[3]

    if _old_name != _new_name or \
            _old_value != _new_value:
        cursor.execute("""
            update property_features
            set details_end_date = getdate()
            where id = ?
        """, id)
        cursor.commit()
        cursor.close()
        cnxn.close()
        feature_write_to_db(row[0], row[1], _new_name, _new_value)


def feature_write_to_db(pid, sid, name, value):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    try:
        cursor.execute("""
            INSERT INTO property_features (
                property_id,
                source_id,
                name,
                value)
            VALUES (
                ?, ?, ?, ?)""",
                       pid,
                       sid,
                       name.lower(),
                       value
                       )
        cursor.commit()
        cursor.close()
        cnxn.close()
    except Exception as e:
        logging.warning('Could not query db: {}, {}, {}, {}: {}'.format(pid,
                                                                        sid,
                                                                        name,
                                                                        value,
                                                                        e))
        cursor.close()
        cnxn.close()
        pass
