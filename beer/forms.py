from django import forms
from .models import Similar_beers, Beers_per_style


class Beer_Search(forms.Form):
    beer_name = forms.CharField(
        max_length=200)


class Beer_Select(forms.Form):
    beer_option = forms.ModelChoiceField(required=True, queryset=Similar_beers.objects.none(), widget=forms.RadioSelect())


class Style_Select(forms.Form):
    style_option = forms.ModelChoiceField(required=True, queryset=Beers_per_style.objects.none(), widget=forms.RadioSelect())
