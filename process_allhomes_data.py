from get_geocode_data import *
from get_estimates_data import *
from get_prop_val_data import *
from get_property_data import *
from write_address_data import *
from write_land_values import *
from write_listing_info import *
from write_features_info import *
from write_flags_info import *
from write_past_sales_info import *
from write_property_dates import *
from write_geocode_data import *
from write_estimates_info import *


def process_allhomes_data(url):
    result_url = url

    logging.info('Getting info for: {}'.format(result_url))
    logging.debug('Getting soup data.')
    soup = get_allhomes_listing_data(result_url)
    logging.debug('Getting address data.')
    address = get_address_data(soup, result_url)
    logging.debug('Getting icon data.')
    icon_data = get_listing_icon_data(soup)
    logging.debug('Getting key info data.')
    key_info = get_key_details_data(soup)
    logging.debug('Getting listing data.')
    listing_info = get_current_listing_data(soup)
    logging.debug('Getting flags data.')
    flags = get_property_flags(soup)
    logging.debug('Getting dates data.')
    listing_dates = get_listing_dates(soup)
    logging.debug('Getting past sales data.')
    past_sales = get_past_sales_data(soup)
    logging.debug('Getting land values data.')
    land_values = get_land_values(key_info)
    logging.debug('Getting price.')
    price = get_price(soup)
    logging.debug('Getting Domain estimates data.')
    domain_estimates = get_estimates_data(result_url)

    url = result_url

    # Define the source id
    source_id = 1

    logging.debug('Updating database.')

    # Check whether the address is in the database
    # If yes: get the maximum id of the property (as details may have changed over time)
    # If no: write the address details to the database
    logging.debug('Updating address details in database.')
    if address:
        in_db = get_existing_address_data(address)
        if in_db:
            property_id = in_db
        else:
            property_id = get_new_property_id(data=address,
                                              pid=listing_info['property_id'] or 9999,
                                              sid=source_id)

        # # Check if prop val in db, no get new data
        # logging.debug('Getting Property Value estimates data.')
        # propval_check = check_in_db(pid=property_id,
        #                             sid=5)
        # if propval_check == 1:
        #     propval_estimates = None
        # else:
        #     propval_estimates = get_prop_val_data(address)

        # Update land values
        logging.debug('Updating land values details in database.')
        if land_values:
            lv_in_db = lv_check_in_db(property_id, source_id)
            lv_id = None
            if lv_in_db:
                lv_id = lv_in_db
                lv_details_changed(lv_id, land_values)
            else:
                lv_write_to_db(property_id, source_id, land_values)

        # Update listing details
        logging.debug('Updating listing info in database.')
        if listing_info:
            listing_in_db = list_check_in_db(property_id, source_id)
            listing_id = None
            if listing_in_db:
                listing_id = listing_in_db
                list_details_changed(listing_id, result_url, listing_info)
            else:
                list_write_to_db(property_id, source_id, result_url, listing_info)

        # Update property features info (icon data)
        logging.debug('Updating icon data in database.')
        if icon_data:
            for key, value in icon_data.items():
                feature_name = key.lower()
                feature_value = value
                feature_in_db = feature_check_in_db(property_id, source_id, key)
                feature_id = None
                if feature_in_db:
                    feature_id = feature_in_db
                    feature_details_changed(feature_id, key, value)
                else:
                    feature_write_to_db(property_id, source_id, key, value)

        # Update property features info (key info)
        logging.debug('Updating key info data in database.')
        if key_info:
            for key, value in key_info.items():
                feature_name = key.lower()
                feature_value = value
                feature_in_db = feature_check_in_db(property_id, source_id, key)
                feature_id = None
                if feature_in_db:
                    feature_id = feature_in_db
                    feature_details_changed(feature_id, key, value)
                else:
                    feature_write_to_db(property_id, source_id, key, value)

        # Update property features info (price)
        logging.debug('Updating price data in database.')
        if price:
            for key, value in price.items():
                feature_name = key.lower()
                feature_value = value
                feature_in_db = feature_check_in_db(property_id, source_id, key)
                feature_id = None
                if feature_in_db:
                    feature_id = feature_in_db
                    feature_details_changed(feature_id, key, value)
                else:
                    feature_write_to_db(property_id, source_id, key, value)

        # Update property flags info
        logging.debug('Updating flags data in database.')
        if flags:
            for key, value in flags.items():
                flag_name = key.lower()
                flag_value = value
                flag_in_db = flag_check_in_db(property_id, source_id, key)
                flag_id = None
                if flag_in_db:
                    flag_id = flag_in_db
                    flag_details_changed(flag_id, key, value)
                else:
                    flag_write_to_db(property_id, source_id, key, value)

        # Update past sales
        logging.debug('Updating past sales data in database.')
        if past_sales:
            for ps in past_sales:
                ps_in_db = past_sales_check_in_db(property_id, source_id, ps['contract_date'])
                ps_id = None
                if ps_in_db:
                    pass
                else:
                    past_sales_write_to_db(property_id, source_id, ps)

        # Update property dates
        logging.debug('Updating property dates in database.')
        if listing_dates:
            for key, value in listing_dates.items():
                date_name = key.lower()
                date_value = value
                date_in_db = dates_check_in_db(property_id, source_id, key)
                date_id = None
                if date_in_db:
                    date_id = date_in_db
                    dates_details_changed(date_id, key, value)
                else:
                    dates_write_to_db(property_id, source_id, key, value)

        # Get existing or new geocode data
        formatted_adr_str = None
        try:
            formatted_adr_str = address['address_street_num'] + ' ' + \
                                address['address_street_name'] + ' ' + \
                                address['address_street_type'] + ' ' + \
                                address['address_suburb'] + ' ' + \
                                address['address_state']
        except KeyError:
            logging.warning('Cannot check for geocode: {}'.format(result_url))
            pass

        existing_geocode = None
        new_geocode = None
        updated_geocode = None
        if formatted_adr_str:
            existing_geocode = get_existing_geocode_data(formatted_adr_str)

        if existing_geocode:
            pass
        else:
            if formatted_adr_str:
                new_geocode = get_geocode(formatted_adr_str)
                if new_geocode:
                    geocode_data = {
                        'lat': new_geocode['lat'],
                        'lon': new_geocode['lng'],
                        'name': formatted_adr_str
                    }
                    # TODO: Change hardcoded sid to query sources table
                    write_new_geocode(sid=3,
                                      data=geocode_data)
                    updated_geocode = get_existing_geocode_data(formatted_adr_str)

        # Add geocode_id to properties table
        if existing_geocode or updated_geocode:
            gid = None
            if existing_geocode:
                gid = existing_geocode['id']
            elif updated_geocode:
                gid = updated_geocode['id']
            update_properties(gid=gid,
                              data=address)

        # Get estimates data from Domain if available
        logging.debug('Updating Domain estimates data in database.')
        if domain_estimates:
            for key, value in domain_estimates.items():
                estimate_name = key.lower()
                estimate_value = value
                estimate_in_db = estimate_check_in_db(pid=property_id,
                                                      sid=2,
                                                      name=key)
                if estimate_in_db:
                    est_id = estimate_in_db
                    estimate_details_changed(est_id, key, value)
                else:
                    estimate_write_to_db(pid=property_id,
                                         sid=2,
                                         name=key,
                                         value=value)

        # # Get estimate from Property Value
        # logging.debug('Updating Property Value estimates data in database.')
        # if propval_estimates:
        #     for key, value in propval_estimates.items():
        #         estimate_name = key.lower()
        #         estimate_value = value
        #         estimate_in_db = estimate_check_in_db(pid=property_id,
        #                                               sid=5,
        #                                               name=key)
        #         if estimate_in_db:
        #             pass
        #         else:
        #             estimate_write_to_db(pid=property_id,
        #                                  sid=5,
        #                                  name=key,
        #                                  value=value)
