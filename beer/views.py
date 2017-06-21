from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from .brewerydb_API_handling import Beer_lookup
from .models import Beers, Styles
from .forms import Beer_Search


def index(request):
    if request.method == 'POST':
        form = Beer_Search(request.POST)
        form.fields['beer_name'].label = 'Please enter a beer name'
        if form.is_valid():
            beer_name_input = form.cleaned_data['beer_name']
            new_search = Beer_lookup()
            response = new_search.beer(beer_name_input)
            return redirect(response[0], response[1])
    else:
        form = Beer_Search()
        form.fields['beer_name'].label = 'Please enter a beer name'
        context = {'hello': 'beerlin index',
               'form': form}
        return render(request, 'beer/index.html', context)


def beer_detail(request, beer_name):
    beer = Beers.objects.get(name=beer_name)
    context = {'hello': "Beer detail page",
               'beer': beer}
    return render(request, 'beer/detail.html', context)


def similar_beers(request, beer_name):
    return HttpResponse("This is a list of beers called %s" % beer_name)


def styles(request):
    return HttpResponse("This is the list of beer styles.")


def style_detail(request, style_name):
    return HttpResponse(
        "This is the list of beers for style %s" % style_name)


def styles_in_beer(request, beer_name):
    return HttpResponse(
        "These are the different styles of beer %s. Please select one" % beer_name)


def beer_not_found(request, beer_name):
    return HttpResponse(
        "Sorry, I couldn't find the beer %s, please try again" % beer_name)
# Create your views here.
