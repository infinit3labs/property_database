

def get_search_page_url(page_num=1):
    _page_num = page_num
    _search_url = 'https://www.allhomes.com.au/sale/search?' \
                  'sort=newest-listing' \
                  '&' \
                  'page={}' \
                  '&' \
                  'region=canberra-act&beds=2-'.format(_page_num)
    # _search_url = \
    #     'https://www.allhomes.com.au/sale/search?' \
    #     'sort=newest-listing' \
    #     '&' \
    #     'page={}' \
    #     '&' \
    #     'district=' \
    #     'belconnen-act,' \
    #     'greater-queanbeyan-queanbeyan-region-nsw,' \
    #     'south-canberra-act,' \
    #     'north-canberra-act,' \
    #     'weston-creek-act,' \
    #     'woden-valley-act' \
    #     '&' \
    #     'suburb=' \
    #     'acton-act-2601,' \
    #     'aranda-act-2614,' \
    #     'braddon-act-2612,' \
    #     'bruce-act-2617,' \
    #     'campbell-act-2612,' \
    #     'chifley-act-2606,' \
    #     'cook-act-2614,' \
    #     'curtin-act-2605,' \
    #     'dickson-act-2602,' \
    #     'downer-act-2602,' \
    #     'garran-act-2605,' \
    #     'giralang-act-2617,' \
    #     'griffith-act-2603,' \
    #     'hawker-act-2614,' \
    #     'holt-act-2615,' \
    #     'hughes-act-2605,' \
    #     'inner-north-act-2601,' \
    #     'kaleen-act-2617,' \
    #     'kambah-act-2902,' \
    #     'kingston-act-2604,' \
    #     'lyneham-act-2602,' \
    #     'lyons-act-2606,' \
    #     'macquarie-act-2614,' \
    #     'mawson-act-2607,' \
    #     'melba-act-2615,' \
    #     'o-connor-act-2602,' \
    #     'pearce-act-2607,' \
    #     'phillip-act-2606,' \
    #     'reid-act-2612,' \
    #     'turner-act-2612,' \
    #     'watson-act-2602' \
    #     '&' \
    #     'propertytypes=house,townhouse,unit-apartment,other,duplex' \
    #     '&' \
    #     'price=-620000' \
    #     '&' \
    #     'beds=2-' \
    #     '&' \
    #     'status=for-sale,under-offer,sold'.format(_page_num)
    return _search_url


# print(get_search_page_url())
