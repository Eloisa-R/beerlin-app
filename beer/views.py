from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from .models import Beers
from .forms import Beer_Search


def index(request):
    if request.method == 'POST':
        form = Beer_Search(request.POST)
        form.fields['beer_name'].label = 'Please enter a beer name'
        if form.is_valid():
            beer_name_input = form.cleaned_data['beer_name']
            return redirect('beer_detail', beer_name=beer_name_input)
    else:
        form = Beer_Search()
        form.fields['beer_name'].label = 'Please enter a beer name'
        context = {'hello': 'beerlin index',
               'form': form}
        return render(request, 'beer/index.html', context)


def beer_detail(request, beer_name):
    list_beers_added = Beers.objects.all()
    context = {'hello': "Beer detail page",
               'list_beers_added': list_beers_added}
    return render(request, 'beer/detail.html', context)


def similar_beers(request, beer_name):
    return HttpResponse("This is a list of beers called %s" % beer_name)


def styles(request):
    return HttpResponse("This is the list of beer styles.")


def style_detail(request, style_name):
    return HttpResponse(
        "This is the list of beers for style %s" % style_name)
# Create your views here.
