from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

from .models import Beers


def index(request):
    list_beers_added = Beers.objects.all()
    context = {'hello': "beerlin index.",
               'list_beers_added': list_beers_added}
    return render(request, 'beer/index.html', context)


def beer_detail(request, beer_name):
    return HttpResponse("This is the detail page for beer %s" % beer_name)


def similar_beers(request, beer_name):
    return HttpResponse("This is a list of beers called %s" % beer_name)


def styles(request):
    return HttpResponse("This is the list of beer styles.")


def style_detail(request, style_name):
    return HttpResponse(
        "This is the list of beers for style %s" % style_name)
# Create your views here.
