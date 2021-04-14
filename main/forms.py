from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


class PricePredictionForm(forms.Form):
    flat_type = forms.IntegerField()
    level_type = forms.IntegerField()
    remaining_lease = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    area = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(300)])
    town = forms.IntegerField()


class FavTownForm(forms.Form):
    town_id = forms.IntegerField()
    is_unfav = forms.BooleanField(required=False)
