from django import forms


class Beer_Search(forms.Form):
    beer_name = forms.CharField(
        max_length=200)
