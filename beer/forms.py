import re
from django import forms
from .models import Similar_beers, Beers_per_style
from django.core.exceptions import ValidationError


def validate_search_input(value):
    eval = re.search("[\w0-9]+", value)
    if eval is None:
        raise ValidationError(
            ('%(value)s is not a valid beer name'),
            params={'value': value},)


class Beer_Search(forms.Form):
    beer_name = forms.CharField(
        max_length=200, validators=[validate_search_input])


class Beer_Select(forms.Form):
    beer_option = forms.ModelChoiceField(
        required=True, queryset=Similar_beers.objects.none(),
        widget=forms.RadioSelect())


class Style_Select(forms.Form):
    style_option = forms.ModelChoiceField(
        required=True, queryset=Beers_per_style.objects.none(),
        widget=forms.RadioSelect())
