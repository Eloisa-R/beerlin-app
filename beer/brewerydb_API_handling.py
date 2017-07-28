import requests
import collections

from .models import Similar_beers, Beers_per_style, Beers, Styles, Breweries
from beerlin.base_settings import API_key_value


class BeerLookup:

    API_key = API_key_value

    url = 'http://api.brewerydb.com/v2/beers/?key='

    base_url = ''

    raw_response = {}

    res_num = 0

    mono_beer_json = collections.OrderedDict(
        [('Name', ['not found', 'name']),
         ('Style_name', ['not found', 'style', 'name']),
         ('Style_id', [0, 'styleId']),
         ('Min_Alcohol', [0.0, 'style', 'abvMin']),
         ('Max_Alcohol', [0.0, 'style', 'abvMax']),
         ('Min_Bitterness', [0, 'style', 'ibuMin']),
         ('Max_Bitterness', [0, 'style', 'ibuMax']),
         ('Description', ['not found', 'style', 'description']),
         ('Name_display', ['not found', 'nameDisplay'])]
    )

    breweries_json = collections.OrderedDict(
        [('Name', ['not found', 'brewery', 'name']),
         ('Location_type', ['not found', 'locationTypeDisplay']),
         ('Brand_classification', ['not found', 'brewery',
                                   'brandClassification']),
         ('Website', ['not found', 'brewery', 'website']),
         ('Is_organic', ['N', 'brewery', 'isOrganic']),
         ('Longitude', [0.000000, 'longitude']),
         ('Latitude', [0.000000, 'latitude']),
         ('Address', ['not available yet', 'streetAddress'])]
    )

    breweries_dict = {}

    style_id = [0, 'id']

    beer_json_data = {}

    temp_json_data = {}

    similar_set = set()

    similar_beers_set = set()

    beer_json_response = {}

    styles_dict = {}

    style_detail_dict = {}

    '''Main function: makes a call to the API using the beer name and
    depending on the response it redirects to different functions'''

    def beer(self, name):
        setattr(BeerLookup, 'base_url', BeerLookup.url + BeerLookup.API_key)
        beer_response = requests.get(BeerLookup.base_url,
                                     params={'name': name}).json()
        try:
            setattr(BeerLookup, 'res_num', beer_response['totalResults'])
        except KeyError:
            try:
                response = BeerLookup.pick_right_beer(self, name)
            except KeyError:
                return ['beer_not_found', name]
            else:
                return response
        else:
            setattr(BeerLookup, 'raw_response', beer_response)
            if BeerLookup.res_num == 1:
                BeerLookup.set_mono_beer_json_data(self)
                BeerLookup.lookup(self)
                BeerLookup.search_similar_beers(self)
                setattr(BeerLookup, 'raw_response', {})
                beer_name = BeerLookup.beer_json_response.get('Name')
                setattr(BeerLookup, 'beer_json_response', {})
                return ['beer_detail', beer_name]
            else:
                response = BeerLookup.show_styles(self, name)
                setattr(BeerLookup, 'raw_response', {})
                return response

    '''Once we have the json response of a unique beer,
    retrieve the data from it using a json helper function,
    then create a record in the Styles table if it doesn't exist and
    a record in the Beers table with the style_id foreign key'''

    def lookup(self):
        for key, value in BeerLookup.mono_beer_json.items():
            BeerLookup.beer_json_response[key] = BeerLookup.json_helper(
                self, BeerLookup.beer_json_data, value)
        new_entry_obj, created = Styles.objects.get_or_create(defaults={
            'style_id': BeerLookup.beer_json_response.get('Style_id'),
            'style_name': BeerLookup.beer_json_response.get('Style_name'),
            'description': BeerLookup.beer_json_response.get('Description')},
            style_id__exact=BeerLookup.beer_json_response.get(
                'Style_id'),
            style_name__iexact=BeerLookup.beer_json_response.get(
                'Style_name'),
            description__iexact=BeerLookup.beer_json_response.get(
                'Description'))
        new_entry_obj.beers_set.get_or_create(defaults={
            'name': BeerLookup.beer_json_response.get('Name'),
            'display_name': BeerLookup.beer_json_response.get('Name_display'),
            'min_alcohol': BeerLookup.beer_json_response.get('Min_Alcohol'),
            'max_alcohol': BeerLookup.beer_json_response.get('Max_Alcohol'),
            'min_bitter': BeerLookup.beer_json_response.get('Min_Bitterness'),
            'max_bitter': BeerLookup.beer_json_response.get(
                'Max_Bitterness')},
            name__iexact=BeerLookup.beer_json_response.get('Name'))
        setattr(BeerLookup, 'beer_json_data', {})

    '''If the Beer endopoint doesn't send the beer data, then we use the Search
    endpoint to check if the name we entered is part of a beer name and not
    the whole thing. I.e. "guinness" is not a beer name,
    but "guinness draught" is.'''

    def pick_right_beer(self, name):
        search_response = requests.get(
            'http://api.brewerydb.com/v2/search?q=' + str(
                name) + '&type=beer&key=' + BeerLookup.API_key).json()
        for item in search_response['data']:
            BeerLookup.similar_beers_set.add(
                BeerLookup.json_helper(
                    self, item, BeerLookup.mono_beer_json.get(
                        'Name_display')))
        for item in BeerLookup.similar_beers_set:
            Similar_beers.objects.get_or_create(defaults={
                'common_name': name,
                'beer_name': item},
                common_name__iexact=name,
                beer_name__iexact=item)
        setattr(BeerLookup, 'similar_beers_set', set())
        return ['similar_beers', name]

    '''If the response is for one beer, the data we need is in the first element
    of 'data' so we need to store that in the variable that we'll use in the
    rest of the functions  '''

    def set_mono_beer_json_data(self):
        setattr(BeerLookup, 'beer_json_data',
                BeerLookup.raw_response['data'][0])

    ''' Function to define the data of the response that we want to use
    in the rest of the functions'''

    def set_beer_json_data(self, user_beer_json_data):
        setattr(BeerLookup, 'beer_json_data',
                user_beer_json_data)

    '''If one of the fields we look for is not present in the json
    we'll get a KeyError exception. To avoid that, each "level" is
    wrapped around a try except block. If the field doesn't exist,
    the value of the variable will be the default one for that field,
    which is stored in the first element of json_ind_list '''

    def json_helper(self, temp_json_data, json_ind_list):
        setattr(BeerLookup, 'temp_json_data', temp_json_data)
        for item in json_ind_list[1:]:
            try:
                result = BeerLookup.temp_json_data[item]
            except KeyError:
                result = json_ind_list[0]
                break
            else:
                setattr(BeerLookup, 'temp_json_data', result)
        return result

    '''To offer a sample of other beers within the same style as the
        one selected, we use the style_id to retrieve all beers within
    that style. Then we create records for those beers in the
    Beers_per_style table'''

    def search_similar_beers(self):
        similar_beers_response = requests.get(
            BeerLookup.base_url,
            params={'styleId': BeerLookup.beer_json_response.get(
                'Style_id')}).json()
        for item in similar_beers_response['data']:
            BeerLookup.similar_set.add(BeerLookup.json_helper(
                self, item, BeerLookup.mono_beer_json.get(
                    'Name_display')))
        recent_entry = Styles.objects.get(
            style_id=BeerLookup.beer_json_response.get('Style_id'))
        for item in BeerLookup.similar_set:
            recent_entry.beers_per_style_set.get_or_create(
                defaults={'beer_name': item}, beer_name__iexact=item)
        setattr(BeerLookup, 'similar_set', set())

    '''If there are several results when we try to retrieve data of a
    beer in particular, it's because there are beers with the same name
    but different styles. This function scans through the json to store
    the styles and styles ids. Then we create records for them in the
    Style table and link the style to the beer name in the Beers_per_style
    table '''

    def show_styles(self, beer_name):
        BeerLookup.set_beer_json_data(self, BeerLookup.raw_response['data'])
        for item in BeerLookup.beer_json_data:
            style_id = BeerLookup.json_helper(
                self, item, BeerLookup.mono_beer_json.get('Style_id'))
            style_name = BeerLookup.json_helper(
                self, item, BeerLookup.mono_beer_json.get('Style_name'))
            if style_id != 'not found' and style_name != 'not found':
                BeerLookup.styles_dict[style_id] = style_name
        for key, value in BeerLookup.styles_dict.items():
            styobj, created = Styles.objects.get_or_create(
                defaults={'style_id': key, 'style_name': value},
                style_id__exact=key, style_name__iexact=value)
            styobj.beers_per_style_set.get_or_create(
                defaults={'beer_name': beer_name}, beer_name__iexact=beer_name)
        setattr(BeerLookup, 'beer_json_data', {})
        setattr(BeerLookup, 'styles_dict', {})
        return ['styles_in_beer', beer_name]

    '''The user sees the different styles that the beer can have thanks to
    the previous function. When he/she chooses one, this function retrieves
    the info of that beer with the style selected'''

    def select_by_style(self, beer_name, style_id):
        setattr(BeerLookup, 'base_url', BeerLookup.url + BeerLookup.API_key)
        styles_response = requests.get(BeerLookup.base_url,
                                       params={'name': beer_name,
                                               'styleId': style_id}).json()
        setattr(BeerLookup, 'raw_response', styles_response)
        BeerLookup.set_mono_beer_json_data(self)
        BeerLookup.lookup(self)
        BeerLookup.search_similar_beers(self)
        beer_name = BeerLookup.beer_json_response.get(
            'Name')
        setattr(BeerLookup, 'raw_response', {})
        setattr(BeerLookup, 'beer_json_response', {})
        return ['beer_detail', beer_name, style_id]

    '''Function that retrieves all the styles of beer. It scans the
    json to retrieve style name and description and store it in the
    Styles table. All the styles are displayed to the user'''

    def styles(self):
        styles_response = requests.get(
            'http://api.brewerydb.com/v2/styles/?key=' +
            BeerLookup.API_key).json()
        for item in styles_response['data']:
            BeerLookup.styles_dict[BeerLookup.json_helper(
                self, item, BeerLookup.style_id)] = [BeerLookup.json_helper(
                    self, item, BeerLookup.mono_beer_json.get('Name')),
                BeerLookup.json_helper(
                    self, item, BeerLookup.mono_beer_json.get(
                        'Description')[1:])]
        for key, value in BeerLookup.styles_dict.items():
            Styles.objects.get_or_create(defaults={
                'style_id': key, 'style_name': value[0],
                'description': value[1]},
                style_id__exact=key,
                style_name__iexact=value[0],
                description__iexact=value[1])
        setattr(BeerLookup, 'styles_dict', {})
        return Styles.objects.all().order_by('style_name')

    '''Once the user has selected a style of beer, we retrieve
    information on that style, like the name of all the beers in
    that style and the description again in case it differs from
    the general one'''

    def style_detail(self, style_id, style_name):
        setattr(BeerLookup, 'base_url', BeerLookup.url + BeerLookup.API_key)
        beers_style_response = requests.get(BeerLookup.base_url,
                                            params={
                                                'styleId': style_id}).json()
        for item in beers_style_response['data']:
            BeerLookup.style_detail_dict[BeerLookup.json_helper(
                self, item, BeerLookup.mono_beer_json.get(
                    'Name_display'))] = BeerLookup.json_helper(
                self, item, BeerLookup.mono_beer_json.get('Description'))

        for key, value in BeerLookup.style_detail_dict.items():
            styobj, created = Styles.objects.get_or_create(
                defaults={'style_id': style_id,
                          'style_name': style_name,
                          'description': value},
                style_id__exact=style_id,
                style_name__iexact=style_name,
                description__iexact=value)
            styobj.beers_per_style_set.get_or_create(
                defaults={'beer_name': key}, beer_name__iexact=key)
        setattr(BeerLookup, 'style_detail_dict', {})

    def get_breweries(self):
        response = requests.get(
            'http://api.brewerydb.com/v2/locations/?key=' +
            str(BeerLookup.API_key), params={'region': 'Berlin'}).json()
        for item in response['data']:
            for key, value in BeerLookup.breweries_json.items():
                BeerLookup.breweries_dict[key] = BeerLookup.json_helper(
                    self, item, value)
            Breweries.objects.get_or_create(
                defaults={
                    'name': BeerLookup.breweries_dict.get('Name'),
                    'location_type': BeerLookup.breweries_dict.get(
                        'Location_type'),
                    'brand_classification': BeerLookup.breweries_dict.get(
                        'Brand_classification'),
                    'website': BeerLookup.breweries_dict.get('Website'),
                    'is_organic': BeerLookup.breweries_dict.get('Is_organic'),
                    'longitude': BeerLookup.breweries_dict.get('Longitude'),
                    'latitude': BeerLookup.breweries_dict.get('Latitude'),
                    'address': BeerLookup.breweries_dict.get('Address')},
                name__iexact=BeerLookup.breweries_dict.get('Name'))
            setattr(BeerLookup, 'breweries_dict', {})
            setattr(BeerLookup, 'beer_json_data', {})
            setattr(BeerLookup, 'temp_json_data', {})
