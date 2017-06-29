from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from .brewerydb_API_handling import Beer_lookup
from .models import Beers, Styles, Similar_beers, Beers_per_style
from . import forms


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
                   'other_method': other_method}
        return render(request, 'beer/index.html', context)


def beer_detail(request, beer_name, style_id=None):
    if style_id is not None:
        styles_beer = Styles.objects.get(style_id=style_id)
        beer = styles_beer.beers_set.get(name=beer_name)
    else:
        beer = Beers.objects.get(name=beer_name)
    context = {'hello': "Beer detail page",
               'beer': beer}
    return render(request, 'beer/detail.html', context)


def similar_beers(request, beer_name):
    if request.method == 'POST':
        select_form = forms.Beer_Select(request.POST)
        select_form.fields['beer_option'].queryset = Similar_beers.objects.filter(
            common_name__iexact=beer_name)
        context = {'title': 'Pick the right beer',
                   'text': 'There are several beers with this name, please choose one.',
                   'select_form': select_form}
        if select_form.is_valid():
            selected_beer = select_form.cleaned_data['beer_option'].beer_name
            new_search = Beer_lookup()
            response = new_search.beer(selected_beer)
            return redirect(response[0], response[1])
    else:
        select_form = forms.Beer_Select()
        select_form.fields['beer_option'].queryset = Similar_beers.objects.filter(
            common_name__iexact=beer_name)
        context = {'title': 'Pick the right beer',
                   'text': 'There are several beers with this name, please choose one.',
                   'select_form': select_form}
        return render(request, 'beer/similar_beers.html', context)


def styles(request):
    new_search = Beer_lookup()
    style_search = new_search.styles()
    context = {'title': 'This is the list of beer styles',
               'style_search': style_search}
    return render(request, 'beer/styles.html', context)


def style_detail(request, style_name, style_id):
    new_search = Beer_lookup()
    new_search.style_detail(style_id, style_name)
    style_obj = Styles.objects.get(style_id__exact= style_id)
    beers = style_obj.beers_per_style_set.all()
    context = {'title': 'Detail view for this style',
               'beers': beers,
               'style_obj': style_obj}
    return render(request, 'beer/style_detail.html', context)


def styles_in_beer(request, beer_name):
    if request.method == 'POST':
        select_form = forms.Style_Select(request.POST)
        select_form.fields['style_option'].queryset = Beers_per_style.objects.filter(
            beer_name__iexact=beer_name)
        context = {'title': 'Pick the right style',
                   'text': 'There are several beers with this name that have different styles, please pick one.',
                   'select_form': select_form}
        if select_form.is_valid():
            selected_beer = select_form.cleaned_data['style_option']
            new_search = Beer_lookup()
            response = new_search.select_by_style(
                selected_beer.beer_name, selected_beer.style_id.style_id)
            return redirect(response[0], response[1], response[2])
    else:
        select_form = forms.Style_Select()
        select_form.fields['style_option'].queryset = Beers_per_style.objects.filter(
            beer_name__iexact=beer_name)
        context = {'title': 'Pick the right style',
                   'text': 'There are several beers with this name that have different styles, please pick one.',
                   'select_form': select_form}
        return render(request, 'beer/styles_in_beer.html', context)


def beer_not_found(request, beer_name):
    return HttpResponse(
        "Sorry, I couldn't find the beer %s, please try again" % beer_name)
# Create your views here.
