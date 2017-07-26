from django.shortcuts import render, redirect

from .brewerydb_API_handling import Beer_lookup
from .models import Beers, Styles, Similar_beers, Beers_per_style, Breweries
from . import forms
from collections import defaultdict
from beerlin import base_settings

def index(request):
    if request.method == 'POST':
        form = forms.Beer_Search(request.POST)
        form.fields['beer_name'].label = 'Please enter a beer name'
        if form.is_valid():
            beer_name_input = form.cleaned_data['beer_name']
            new_search = Beer_lookup()
            response = new_search.beer(beer_name_input)
            return redirect(response[0], response[1])
        else:
            form = forms.Beer_Search()
            form.fields['beer_name'].label = 'Please enter a beer name'
            other_method = 'Or search per category'
            context = {'hello': 'beerlin',
                       'form': form,
                       'other_method': other_method,
                       'invalid': 'Invalid beer name. Please try again.'}
            return render(request, 'beer/index.html', context)
    else:
        form = forms.Beer_Search()
        form.fields['beer_name'].label = 'Please enter a beer name'
        other_method = 'Or search per category'
        context = {'hello': 'beerlin',
                   'form': form,
                   'other_method': other_method}
        return render(request, 'beer/index.html', context)


def beer_detail(request, beer_name, style_id=None):
    if style_id is not None:
        styles_beer = Styles.objects.get(style_id=style_id)
        beer = styles_beer.beers_set.get(name__iexact=beer_name)
        similar = styles_beer.beers_per_style_set.all()
        similar_list = [item.beer_name for item in similar]
        [similar_list.remove(item) for item in similar_list if beer.name.lower() == item.lower()]
    else:
        beer = Beers.objects.get(name__iexact=beer_name)
        style_id = beer.style_id.style_id
        style_obj = Styles.objects.get(style_id=style_id)
        similar = style_obj.beers_per_style_set.all()
        similar_list = [item.beer_name for item in similar]
        [similar_list.remove(item) for item in similar_list if beer.name.lower() == item.lower()]
    context = {'hello': str(beer_name),
               'beer': beer,
               'similar': similar_list}
    return render(request, 'beer/detail.html', context)


def similar_beers(request, beer_name):
    if request.method == 'POST':
        beers = Similar_beers.objects.filter(
            common_name__iexact=beer_name)
        num_col = 2
        rangeb = range(0, num_col)
        select_form = forms.Beer_Select(request.POST)
        select_form.fields['beer_option'].queryset = beers
        context = {'title': 'Pick the right beer',
                   'text': 'There are several beers with this name, please choose one.',
                   'select_form': select_form,
                   'rangeb': rangeb,
                   'num_col': num_col}
        if select_form.is_valid():
            selected_beer = select_form.cleaned_data['beer_option'].beer_name
            new_search = Beer_lookup()
            response = new_search.beer(selected_beer)
            return redirect(response[0], response[1])
        else:
            beers = Similar_beers.objects.filter(
                common_name__iexact=beer_name)
            num_col = 2
            rangeb = range(0, num_col)
            select_form = forms.Beer_Select()
            select_form.fields['beer_option'].queryset = beers
            context = {'title': 'Pick the right beer',
                   'text': 'There are several beers with this name, please choose one.',
                   'select_form': select_form,
                   'rangeb': rangeb,
                   'num_col': num_col,
                   'invalid': 'Please select an option'}
            return render(request, 'beer/similar_beers.html', context)
    else:
        beers = Similar_beers.objects.filter(
            common_name__iexact=beer_name)
        num_col = 2
        rangeb = range(0, num_col)
        select_form = forms.Beer_Select()
        select_form.fields['beer_option'].queryset = beers
        context = {'title': 'Pick the right beer',
                   'text': 'There are several beers with this name, please choose one.',
                   'select_form': select_form,
                   'rangeb': rangeb,
                   'num_col': num_col}
        return render(request, 'beer/similar_beers.html', context)


def styles(request):
    global_dict = defaultdict(list)
    new_search = Beer_lookup()
    style_search = new_search.styles()
    for item in style_search:
        global_dict[item.style_name[0]].append([item.style_id, item.style_name])
    context = {'title': 'Beer styles',
               'text': 'Alphabetical list of beer styles',
               'global_dict': sorted(dict(global_dict).items())}
    return render(request, 'beer/styles.html', context)


def style_detail(request, style_name, style_id):
    if request.method == 'POST':
        form = forms.Beer_Search(request.POST)
        form.fields['beer_name'].label = ''
        if form.is_valid():
            beer_name_input = form.cleaned_data['beer_name']
            new_search = Beer_lookup()
            response = new_search.select_by_style(beer_name_input, style_id)
            return redirect(response[0], response[1], response[2])
        else:
            form = forms.Beer_Search()
            form.fields['beer_name'].label = ''
            new_search = Beer_lookup()
            new_search.style_detail(style_id, style_name)
            style_obj = Styles.objects.get(style_id__exact=style_id)
            beers = style_obj.beers_per_style_set.all()
            num_col = 2
            rangeb = range(0, num_col)
            context = {'title': str(style_name),
                       'beers': beers,
                       'style_obj': style_obj,
                       'rangeb': rangeb,
                       'num_col': num_col,
                       'form': form}
            return render(request, 'beer/style_detail.html', context)
    else:
        form = forms.Beer_Search()
        form.fields['beer_name'].label = ''
        new_search = Beer_lookup()
        new_search.style_detail(style_id, style_name)
        style_obj = Styles.objects.get(style_id__exact=style_id)
        beers = style_obj.beers_per_style_set.all()
        num_col = 2
        rangeb = range(0, num_col)
        context = {'title': str(style_name),
                   'beers': beers,
                   'style_obj': style_obj,
                   'rangeb': rangeb,
                   'num_col': num_col,
                   'form': form}
        return render(request, 'beer/style_detail.html', context)


def styles_in_beer(request, beer_name):
    if request.method == 'POST':
        select_form = forms.Style_Select(request.POST)
        styles = Beers_per_style.objects.filter(
            beer_name__iexact=beer_name)
        num_col = 2
        rangeb = range(0, num_col)
        select_form.fields['style_option'].queryset = styles
        context = {'title': 'Pick the right style',
                   'text': 'There are several beers with this name that have different styles, please pick one.',
                   'select_form': select_form,
                   'rangeb': rangeb,
                   'num_col': num_col}
        if select_form.is_valid():
            selected_beer = select_form.cleaned_data['style_option']
            new_search = Beer_lookup()
            response = new_search.select_by_style(
                selected_beer.beer_name, selected_beer.style_id.style_id)
            return redirect(response[0], response[1], response[2])
        else:
            select_form = forms.Style_Select()
            styles = Beers_per_style.objects.filter(
                beer_name__iexact=beer_name)
            num_col = 2
            rangeb = range(0, num_col)
            select_form.fields['style_option'].queryset = styles
            context = {'title': 'Pick the right style',
                   'text': 'There are several beers with this name that have different styles, please pick one.',
                   'select_form': select_form,
                   'rangeb': rangeb,
                   'num_col': num_col,
                   'invalid': 'Please select an option'}
        return render(request, 'beer/styles_in_beer.html', context)
    else:
        select_form = forms.Style_Select()
        styles = Beers_per_style.objects.filter(
            beer_name__iexact=beer_name)
        num_col = 2
        rangeb = range(0, num_col)
        select_form.fields['style_option'].queryset = styles
        context = {'title': 'Pick the right style',
                   'text': 'There are several beers with this name that have different styles, please pick one.',
                   'select_form': select_form,
                   'rangeb': rangeb,
                   'num_col': num_col}
        return render(request, 'beer/styles_in_beer.html', context)


def beer_not_found(request, beer_name):
    context = {'text': 'Sorry, I couldn\'t find the beer ' + beer_name + ', please try again',
               'subtitle': 'Not found'}
    return render(request, 'beer/beer_not_found.html', context)


def about(request):
    hello = 'Hello there!'
    text = 'The Beerlin project revolves around two great things ' \
    'that work great together: beer and the city of Berlin.' \
    'In the section “Beer search” you can find out about the ' \
    'characteristics of an specific beer by entering its name—especially ' \
    'useful if you are at a restaurant or bar and want to ' \
    'find out more about the beer you see in the menu. If you don’t ' \
    'have an specific name at hand and want to find beers ' \
    'you might like, the “Category search” section shows ' \
    'different styles of beer, the description for each of ' \
    'them and some beer names for that category. Finally, ' \
    'the “Berlin breweries” section shows a list of breweries ' \
    'in the region of Berlin, a bit of information about them ' \
    '(website, type of beer produced, etc.) and their location on a map.'
    context = {'hello': hello, 'text': text}
    return render(request, 'beer/about.html', context)


def breweries(request):
    new_search = Beer_lookup()
    new_search.get_breweries()
    breweries_queryset = Breweries.objects.all()
    title = 'Breweries in Berlin'
    text = 'This is a list of the breweries in the Berlin region. Click on the names to find out more about them.'
    context = {'breweries': breweries_queryset, 'title': title, 'text': text}
    return render(request, 'beer/breweries.html', context)


def breweries_detail(request, brewery_name):
    brewery_obj = Breweries.objects.get(name__iexact=brewery_name)
    map_text = 'Here you can find the brewery:'
    context = {'brewery': brewery_obj, 'map_text': map_text,
    'gkey': base_settings.google_API_value}
    return render(request, 'beer/breweries_detail.html', context)