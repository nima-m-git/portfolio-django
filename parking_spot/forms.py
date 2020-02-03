from django import forms
from .models import Entries



class EntryForm(forms.ModelForm):

    TIME_CHOICES = [(m,f) for m,f in zip(
        [str(i) for i in range(24)], [str(i).zfill(2) for i in range(24)]
        )]
    time = forms.ChoiceField(choices= TIME_CHOICES)

    class Meta:
        model = Entries
        fields = ['spot', 'empty', 'time']
