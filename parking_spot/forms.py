
from django import forms
from .models import Entries, Statistics


TIME_CHOICES = [(m,f) for m,f in zip(
    [str(i) for i in range(24)], [str(i).zfill(2) for i in range(24)]
    )]
TIME_CHOICES.insert(0,('','---'))
time = forms.ChoiceField(choices= TIME_CHOICES)

spots = Entries.objects.only('spot').distinct('spot')
SPOT_CHOICES = [(x,z) for x,z in zip(spots, spots)]

def spot_choices():
    return SPOT_CHOICES


class EntryForm(forms.ModelForm):
    time = time

    class Meta:
        model = Entries
        fields = ['spot', 'empty', 'time']


class TimeForm(forms.Form):
    time = time

class TimeRangeForm(forms.Form):
    From = time
    To = time

class SpotForm(forms.Form):
    spots = forms.MultipleChoiceField(choices=SPOT_CHOICES, widget=forms.CheckboxSelectMultiple)

print(SPOT_CHOICES)