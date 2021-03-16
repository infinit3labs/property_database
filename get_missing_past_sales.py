from connect_db import get_db_connection
import logging


def get_urls_pids():
    # Get urls and property ids of all properties
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""
            select property_id,
                   url
            from property_listings.dbo.listings
            where details_end_date is null
            and property_id not in (
                select property_id
                from property_listings.dbo.past_sales_info
                where datediff(day, contract_date, getdate()) <= 180
                )
        """)
        rows = cursor.fetchall()
        cursor.close()
        cnxn.close()
        if rows:
            return rows
        else:
            logging.warning('No results from query for listings.')
            return None
    except Exception as e:
        cursor.close()
        cnxn.close()
        logging.warning(f'Database query failed for listings details: {e}')
        pass


def get_existing_past_sales(pid):
    cnxn = get_db_connection()
    cursor = cnxn.cursor()
    try:
        cursor.execute("""
        select property_id,
        price,
        contract_date
        from property_listings.dbo.past_sales_info
        where property_id = ?
        """, pid)
        rows = cursor.fetchall()
        cursor.close()
        cnxn.close()
        if rows:
            return rows
        else:
            logging.warning(f'No results from query for past sales: {pid}.')
            return None
    except Exception as e:
        cursor.close()
        cnxn.close()
        logging.warning(f'Database query failed for past sales: {e}: {pid}')
        pass
