from django.test import TestCase
from . import forms
from django.test import Client
from django.core.urlresolvers import reverse
from .brewerydb_API_handling import BeerLookup
from django.test.utils import setup_test_environment
from . import models
from collections import defaultdict
import requests
from beerlin.base_settings import API_key_value


class FormTest(TestCase):

    def test_search_is_only_valid_with_alphanum(self):
        form = forms.Beer_Search({'beer_name': ' '})
        self.assertFalse(form.is_valid())

    def test_non_ASCII(self):
        form = forms.Beer_Search({'beer_name': 'mahou clásica'})
        self.assertTrue(form.is_valid())


class ViewsTest(TestCase):

    def test_index_view(self):
        setup_test_environment()
        client = Client()
        response = client.get(reverse('index'))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['other_method'],
                         'Or search per category')
        self.assertEqual(response.context['hello'], 'beerlin')
        self.assertTrue(response.context, 'form')

    def test_regex(self):
        setup_test_environment()
        client = Client()
        test_set = set()
        for index in range(1, 170):
            test_beers_response = requests.get(
                'http://api.brewerydb.com/v2/beers/?key=' + str(API_key_value),
                params={'styleId': index}).json()
            for item in test_beers_response['data']:
                try:
                    test_set.add(item['nameDisplay'])
                except KeyError:
                    pass

        for item in test_set:
            beer_name_test = item
            try:
                response = client.get(reverse(
                    'beer_not_found', args=(beer_name_test,)))
            except Exception:
                print(item)

    def test_beer_detail_view(self):
        beer_name_test = 'Punk IPA'
        setup_test_environment()
        client = Client()
        new_search = BeerLookup()
        new_search.beer(beer_name_test)
        beer_test = models.Beers.objects.get(name__iexact=beer_name_test)
        response = client.get(reverse('beer_detail', args=(beer_name_test,)))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['hello'], beer_name_test)
        self.assertEqual(response.context['beer'], beer_test)

    def test_beer_detail_view_with_style(self):
        beer_name_test = 'Altbier'
        style_test = '55'
        setup_test_environment()
        client = Client()
        new_search = BeerLookup()
        new_search.select_by_style(beer_name_test, style_test)
        style_obj_test = models.Styles.objects.get(style_id=style_test)
        beer_obj_test = style_obj_test.beers_set.get(
            name__iexact=beer_name_test)
        response = client.get(reverse(
            'beer_detail', args=(beer_name_test, style_test)))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['hello'], beer_name_test)
        self.assertEqual(response.context['beer'], beer_obj_test)

    def test_similar_beers_view(self):
        test_beer_name = 'guinness'
        setup_test_environment()
        client = Client()
        new_search = BeerLookup()
        new_search.beer(test_beer_name)
        test_beers = models.Similar_beers.objects.filter(
            common_name__iexact=test_beer_name)
        test_select_form = forms.Beer_Select()
        test_select_form.fields['beer_option'].queryset = test_beers
        response = client.get(reverse('similar_beers', args=(test_beer_name,)))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Pick the right beer')
        self.assertEqual(response.context['text'],
                         'There are several beers with this name,\
                          please choose one.')
        self.assertQuerysetEqual(
            response.context['select_form'].fields['beer_option'].queryset,
            [repr(ob) for ob
             in test_select_form.fields['beer_option'].queryset],
            ordered=False)

    def test_styles_view(self):
        setup_test_environment()
        client = Client()
        test_global_dict = defaultdict(list)
        new_search = BeerLookup()
        test_style_search = new_search.styles()
        for item in test_style_search:
            test_global_dict[item.style_name[0]].append(
                [item.style_id, item.style_name])
        response = client.get(reverse('styles'))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Beer styles')
        self.assertEqual(response.context['text'],
                         'Alphabetical list of beer styles')
        self.assertEqual(response.context['global_dict'],
                         sorted(dict(test_global_dict).items()))

    def test_style_detail_view(self):
        test_style_name = 'Belgian-Style Dark Strong Ale'
        test_style_id = '64'
        setup_test_environment()
        client = Client()
        new_search = BeerLookup()
        new_search.style_detail(test_style_id, test_style_name)
        test_style_obj = models.Styles.objects.get(
            style_id__exact=test_style_id)
        test_beers = test_style_obj.beers_per_style_set.all()
        response = client.get(reverse(
            'style_detail', args=(test_style_name, test_style_id)))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['title'], test_style_name),
        self.assertQuerysetEqual(response.context['beers'],
                                 [repr(ob) for ob in test_beers],
                                 ordered=False)
        self.assertEqual(response.context['style_obj'], test_style_obj)

    def test_styles_in_beer_view(self):
        test_beer_name = 'Altbier'
        setup_test_environment()
        client = Client()
        test_select_form = forms.Style_Select()
        test_styles = models.Beers_per_style.objects.filter(
            beer_name__iexact=test_beer_name)
        test_select_form.fields['style_option'].queryset = test_styles
        response = client.get(reverse(
            'styles_in_beer', args=(test_beer_name,)))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Pick the right style')
        self.assertEqual(response.context['text'],
                         'There are several beers with this name that have \
                        different styles, please pick one.')
        self.assertQuerysetEqual(
            response.context['select_form'].fields['style_option'].queryset,
            [repr(ob) for ob
             in test_select_form.fields['style_option'].queryset],
            ordered=False)

    def test_beer_not_found_view(self):
        test_non_beer = 'qovoiEWV'
        client = Client()
        setup_test_environment()
        response = client.get(reverse('beer_not_found', args=(test_non_beer,)))
        self.assertIs(response.status_code, 200)
        self.assertEqual(response.context['text'],
                         'Sorry, I couldn\'t find the beer ' +
                         test_non_beer + ', please try again')
        self.assertEqual(response.context['subtitle'], 'Not found')


class API_handle_test(TestCase):

    def test_beer_func_mono(self):
        test_beer_name = 'rochefort 8'
        test_search = BeerLookup()
        response = test_search.beer(test_beer_name)
        self.assertEqual([item.lower() for item in response],
                         ['beer_detail', test_beer_name])

    def test_beer_func_not_found(self):
        test_beer_name = 'ñascmpá'
        test_search = BeerLookup()
        response = test_search.beer(test_beer_name)
        self.assertEqual([item.lower() for item in response],
                         ['beer_not_found', test_beer_name])

    def test_beer_func_similar(self):
        test_beer_name = 'heineken'
        test_search = BeerLookup()
        response = test_search.beer(test_beer_name)
        self.assertEqual([item.lower() for item in response],
                         ['similar_beers', test_beer_name])

    def test_beer_func_several_style(self):
        test_beer_name = 'altbier'
        test_search = BeerLookup()
        response = test_search.beer(test_beer_name)
        self.assertEqual([item.lower() for item in response],
                         ['styles_in_beer', test_beer_name])

    def test_select_by_style(self):
        test_beer_name = 'altbier'
        test_style = '55'
        test_search = BeerLookup()
        response_style = test_search.select_by_style(
            test_beer_name, test_style)
        self.assertEqual(
            [item.lower() for item in response_style],
            ['beer_detail', test_beer_name, test_style])

    def test_select_styles(self):
        test_search = BeerLookup()
        test_styles = test_search.styles()
        self.assertFalse(test_styles is None)

    def test_style_detail(self):
        test_style_name = 'English-Style Brown Ale'
        test_style_id = '12'
        test_search = BeerLookup()
        test_search.style_detail(test_style_id, test_style_name)
        self.assertTrue(models.Styles.objects.filter(
            style_id=test_style_id).exists())


class DBtest(TestCase):

    def test_no_duplicates_in_beer_per_style(self):
        test_dict_1 = defaultdict(list)
        test_dict_2 = defaultdict(list)
        test_beer_name = 'Märkischer Landmann Schwarzbier'
        test_search_1 = BeerLookup()
        test_search_1.beer(test_beer_name)
        objs_in_db_1 = models.Beers_per_style.objects.all()
        for item in objs_in_db_1:
            test_dict_1[item.style_id.style_id].append([item.beer_name])
        test_search_2 = BeerLookup()
        test_search_2.beer(test_beer_name)
        objs_in_db_2 = models.Beers_per_style.objects.all()
        for item in objs_in_db_2:
            test_dict_2[item.style_id.style_id].append([item.beer_name])
        self.assertEqual(test_dict_1, test_dict_2)

    def test_no_duplicates_in_styles(self):
        test_dict_1 = defaultdict(list)
        test_dict_2 = defaultdict(list)
        test_beer_name = 'Altbier'
        test_search_1 = BeerLookup()
        test_search_1.beer(test_beer_name)
        objs_in_db_1 = models.Styles.objects.all()
        for item in objs_in_db_1:
            test_dict_1[item.style_id].append([item.style_name])
        test_search_2 = BeerLookup()
        test_search_2.beer(test_beer_name)
        objs_in_db_2 = models.Styles.objects.all()
        for item in objs_in_db_2:
            test_dict_2[item.style_id].append([item.style_name])
        self.assertEqual(test_dict_1, test_dict_2)

    def test_no_duplicates_in_similar_beers(self):
        test_dict_1 = defaultdict(list)
        test_dict_2 = defaultdict(list)
        test_beer_name = 'Guinness'
        test_search_1 = BeerLookup()
        test_search_1.beer(test_beer_name)
        objs_in_db_1 = models.Similar_beers.objects.all()
        for item in objs_in_db_1:
            test_dict_1[item.common_name].append([item.beer_name])
        test_search_2 = BeerLookup()
        test_search_2.beer(test_beer_name)
        objs_in_db_2 = models.Similar_beers.objects.all()
        for item in objs_in_db_2:
            test_dict_2[item.common_name].append([item.beer_name])
        self.assertEqual(test_dict_1, test_dict_2)

    def test_no_duplicates_in_beers(self):
        test_dict_1 = defaultdict(list)
        test_dict_2 = defaultdict(list)
        test_beer_name_1 = 'rochefort 8'
        test_search_1 = BeerLookup()
        test_search_1.beer(test_beer_name_1)
        objs_in_db_1 = models.Beers.objects.all()
        for item in objs_in_db_1:
            test_dict_1[item.style_id.style_id].append([item.name])
        test_search_2 = BeerLookup()
        test_beer_name_2 = 'Rochefort 8'
        test_search_2.beer(test_beer_name_2)
        objs_in_db_2 = models.Beers.objects.all()
        for item in objs_in_db_2:
            test_dict_2[item.style_id.style_id].append([item.name])
        self.assertEqual(test_dict_1, test_dict_2)
