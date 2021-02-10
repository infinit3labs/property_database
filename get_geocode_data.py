import googlemaps
import config


def get_geocode(formatted_add_str):
    key = config.GMAPS_KEY
    # Format [Str Num] [Street Name] [Street Type] [Suburb] [State]
    gmaps = googlemaps.Client(key=key)

    address = formatted_add_str
    try:
        geocode_result = gmaps.geocode('{}'.format(address))
    except googlemaps.exceptions.ApiError:
        return None
    try:
        result = geocode_result[0]['geometry']['location']
    except IndexError:
        result = None
    return result
