from connect_db import get_db_connection
import logging


def past_sales_check_in_db(pid, sid, contract_date):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()

    try:
        row = cursor.execute("""
            select *
            from (
            select id,
                   row_number() OVER (order by id desc) row_num
            from past_sales_info
            where property_id = ?
            and source_id = ?
            and contract_date = ?) t 
            where row_num = 1
        """, pid, sid, contract_date)
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
                                                                    contract_date,
                                                                    e))
        cursor.close()
        cnxn.close()


def past_sales_write_to_db(pid, sid, data):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    price = 0
    listed_date = None
    contract_date = None
    transfer_date = None
    sale_type = None
    try:
        price = data['price']
    except KeyError:
        price = None
    try:
        listed_date = data['listed_date']
    except KeyError:
        listed_date = None
    try:
        contract_date = data['contract_date']
    except KeyError:
        print('Data must have contract date')
        return None
    try:
        transfer_date = data['transfer_date']
    except KeyError:
        transfer_date = None
    try:
        sale_type = data['sale_type']
    except KeyError:
        sale_type = None

    try:
        cursor.execute("""
            INSERT INTO past_sales_info (
                property_id,
                source_id,
                price,
                list_date,
                contract_date,
                transfer_date,
                sale_type)
            VALUES (
                ?, ?, ?, ?, ?, ?, ?)""",
                       pid,
                       sid,
                       price,
                       listed_date,
                       contract_date,
                       transfer_date,
                       sale_type,
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
