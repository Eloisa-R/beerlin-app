from django.db import models


class Styles(models.Model):
    style_id = models.IntegerField(default=0)
    style_name = models.CharField(max_length=200)


class Beers(models.Model):
    name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    style_id = models.ForeignKey('Styles', on_delete=models.PROTECT)
    min_alcohol = models.FloatField(default=0.0)
    max_alcohol = models.FloatField(default=0.0)
    min_bitter = models.IntegerField(default=0)
    max_bitter = models.IntegerField(default=0)
    description = models.TextField()


class Beers_per_style(models.Model):
    style_id = models.ForeignKey('Styles', on_delete=models.PROTECT)
    beer_name = models.CharField(max_length=200)


class Similar_beers(models.Model):
    common_name = models.CharField(max_length=200)
    beer_name = models.CharField(max_length=200)

# Create your models here.
