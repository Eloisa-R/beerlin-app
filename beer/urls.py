from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'''^(?P<beer_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=\'_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)
        /(?P<style_id>[0-9]+)/detail$''',
        views.beer_detail, name='beer_detail'),
    url(r'''^(?P<beer_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=\'_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)
        /detail$''', views.beer_detail, name='beer_detail'),
    url(r'''^(?P<beer_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=\'_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)/similar$''',
        views.similar_beers, name='similar_beers'),
    url(r'^search/styles/$', views.styles, name='styles'),
    url(r'''^styles/(?P<style_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=\'_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)
        /(?P<style_id>[0-9]+)/$''', views.style_detail, name='style_detail'),
    url(r'''^(?P<beer_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=\'_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)/not_found$''',
        views.beer_not_found, name='beer_not_found'),
    url(r'''^(?P<beer_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)/different_styles$''',
        views.styles_in_beer, name='styles_in_beer'),
    url(r'^about/$', views.about, name='about'),
    url(r'^breweries/$', views.breweries, name='breweries'),
    url(r'''^breweries/(?P<brewery_name>[\w0-9 \-/\(\)""&,#!@\$%\^\*\{\}\[\]
        :;\.,\?~\+=_|\\<>’–¿·ªº¡°™“”‘—\u200e\u202c]+)$''',
        views.breweries_detail, name='breweries_detail'),
]
