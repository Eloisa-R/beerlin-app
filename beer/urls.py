from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<beer_name>[A-Za-z_]+)/$', views.beer_detail, name='beer_detail'),
    url(r'^(?P<beer_name>[A-Za-z_]+)/similar$', views.similar_beers, name='similar_beers'),
    url(r'^(styles)/$', views.styles, name='styles'),
    url(r'^styles/(?P<style_name>[A-Za-z_]+)/$',
        views.style_detail, name='style_detail'),
]
