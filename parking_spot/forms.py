
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


class ComboForm(forms.Form):
    spots = forms.MultipleChoiceField(choices=SPOT_CHOICES, widget=forms.CheckboxSelectMultiple)
    time = forms.ChoiceField(choices= TIME_CHOICES, required=False)
    From = forms.ChoiceField(choices= TIME_CHOICES, required=False)
    To = forms.ChoiceField(choices= TIME_CHOICES, required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        time = cleaned_data.get('time')
        From = cleaned_data.get('From')
        To = cleaned_data.get('To')
        spots = cleaned_data.get('spots')

        if not time and not (From and To):
            raise forms.ValidationError('Please fill in both fields in the set.')
        if time and (From or To):
            raise forms.ValidationError('Please fill in only one field set.')
        if not any([time,From,To]):
            raise forms.ValidationError('Please fill in a field set.')
        if not spots:
            raise forms.ValidationError('Please select at least one spot.')


        



class SpotForm(forms.Form):
    spots = forms.MultipleChoiceField(choices=SPOT_CHOICES, widget=forms.CheckboxSelectMultiple)

