from django import forms
from .models import Entries, Statistics


TIME_CHOICES = [(m,f) for m,f in zip(
    [str(i) for i in range(24)], [str(i).zfill(2) for i in range(24)]
    )]
time = forms.ChoiceField(choices= TIME_CHOICES)

class EntryForm(forms.ModelForm):
    time = time

    class Meta:
        model = Entries
        fields = ['spot', 'empty', 'time']


class TimeForm(forms.Form):
    time = time
