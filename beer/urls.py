import re
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<beer_name>[A-Za-z_0-9 äëïöüáéíóúàèìòùâêîôûßÇæœñ\-/()""&,]+)/(?P<style_id>[0-9]+)/detail$', views.beer_detail, name='beer_detail'),
    url(r'^(?P<beer_name>[A-Za-z_0-9 äëïöüáéíóúàèìòùâêîôûßÇæœñ\-/()""&,]+)/detail$', views.beer_detail, name='beer_detail'),
    url(r'^(?P<beer_name>[A-Za-z_0-9 äëïöüáéíóúàèìòùâêîôûßÇæœñ\-/()""&,]+)/similar$', views.similar_beers, name='similar_beers'),
    url(r'^search/styles/$', views.styles, name='styles'),
    url(r'^styles/(?P<style_name>[A-Za-z_0-9 äëïöüáéíóúàèìòùâêîôûßÇæœñ\-/()""&,]+)/(?P<style_id>[0-9]+)/$',
        views.style_detail, name='style_detail'),
    url(r'^(?P<beer_name>[A-Za-z_0-9 äëïöüáéíóúàèìòùâêîôûßÇæœñ\-/()""&,]+)/not_found', views.beer_not_found, name='beer_not_found'),
    url(r'^(?P<beer_name>[A-Za-z_0-9 äëïöüáéíóúàèìòùâêîôûßÇæœñ\-/()""&,]+)/different_styles', views.styles_in_beer, name='styles_in_beer')
]
