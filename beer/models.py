from django.db import models


class Styles(models.Model):
    style_id = models.IntegerField(default=0)
    style_name = models.CharField(max_length=200)
    description = models.TextField(default='not yet provided')


class Beers(models.Model):
    name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    style_id = models.ForeignKey('Styles', on_delete=models.CASCADE)
    min_alcohol = models.FloatField(default=0.0)
    max_alcohol = models.FloatField(default=0.0)
    min_bitter = models.IntegerField(default=0)
    max_bitter = models.IntegerField(default=0)


class Beers_per_style(models.Model):
    style_id = models.ForeignKey('Styles', on_delete=models.CASCADE)
    beer_name = models.CharField(max_length=200)


class Similar_beers(models.Model):
    common_name = models.CharField(max_length=200)
    beer_name = models.CharField(max_length=200)


class Breweries(models.Model):
    name = models.CharField(max_length=200)
    location_type = models.CharField(max_length=200)
    brand_classification = models.CharField(max_length=200)
    website = models.CharField(max_length=200)
    is_organic = models.CharField(max_length=1)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=200, default='not available yet')
