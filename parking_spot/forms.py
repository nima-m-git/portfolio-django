from django import forms
from .models import Entries, Statistics
from operator import itemgetter


TIME_CHOICES = [(m,f) for m,f in zip(
    [str(i) for i in range(24)], [str(i).zfill(2) for i in range(24)]
    )]
TIME_CHOICES.insert(0,('','---'))
time = forms.ChoiceField(choices= TIME_CHOICES)

spots = Entries.objects.only('spot').distinct('spot')
SPOT_CHOICES = [(x,z) for x,z in zip(spots, spots)]

probabilities = ['{:.2f}'.format(i/100) for i in range(1, 101)][::-1] 
PROBABILITY_CHOICES = [(x,z) for x,z in zip(([i for i in range(1, 101)][::-1]), probabilities)]
PROBABILITY_CHOICES.insert(0,('','---'))
num_entries = Statistics.objects.all().distinct('entries').values_list('entries', flat=True).order_by('entries')
ENTRIES_CHOICES = [(x,z) for x,z in zip(num_entries, num_entries)]
ENTRIES_CHOICES.insert(0,('','---'))
stds = Statistics.objects.all().distinct('std').values_list('std', flat=True).order_by('std')
STD_CHOICES = [(x,z) for x,z in zip(stds, stds)]
STD_CHOICES.insert(0,('','---'))



def spot_choices():
    return SPOT_CHOICES


class EntryForm(forms.ModelForm):
    time = time

    class Meta:
        model = Entries
        fields = ['spot', 'empty', 'time']


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


class TopEntriesForm(forms.Form):
    min_probability = forms.ChoiceField(choices = PROBABILITY_CHOICES, required=False)  
    min_entries = forms.ChoiceField(choices = ENTRIES_CHOICES, required=False)
    standard_deviation = forms.ChoiceField(choices = STD_CHOICES, required=False)     
