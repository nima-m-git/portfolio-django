from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from django_pandas.io import read_frame
import pandas as pd

from parking_spot.models import Entries, Statistics
from .forms import EntryForm, spot_choices as spots, ComboForm, TopEntriesForm
import parking_spot.functions as fx


def index(request):
    return render(request, 'parking_spot/index.html')


def add_entry(request):
    ''' adds an entry to the database '''
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if 'update' in request.POST: #if 'update' button clicked, 'update' value will be in post form
            Stats.update_entries()  #update has novalidate, do not save form when updating
        else:
            form.save()
        return redirect('add_entry')
    else:
        form = EntryForm()
    spots = Entries.objects.distinct('spot')
    return render(request, 'parking_spot/add_entry.html', {'form': form, 'spots': spots})


def view_entries(request):
    ## create dynamic table to be able to change/delete entry
    entries = Entries.objects.all().order_by('-date_added')
    return render(request, 'parking_spot/view_entries.html', {'entries':entries})


class Stats():


    def index(request):
        return render(request, 'parking_spot/stats_index.html')


    def update_entries():
        ''' Deletes 'Statistics' table and repopulates with new Entries '''
        spots = Entries.objects.distinct('spot')
        hours = [str(i).zfill(2) for i in range(24)]
        min_entries = 1
        Statistics.objects.all().delete()
        for spot in spots:
            for hour in hours:
                empty_count = Entries.objects.filter(spot=spot, time=hour, empty=True).count()
                total_count = Entries.objects.filter(spot=spot, time=hour).count()
                if total_count >= min_entries:
                    probability = empty_count/total_count
                    std = (probability*(1-probability)/total_count)**0.5
                else:
                    probability = None
                    std = None
                Statistics(spot=spot, time=hour, probability=probability, entries=total_count, std=std).save()


    def stats_table(request):
        stats = Statistics.objects.all().order_by('spot', 'time')
        return render(request, 'parking_spot/stats_table.html', {'stats':stats})


    def probability_charts(request):
        '''Display selected spots probabilities with visual charts'''
        form = ComboForm(request.POST)
        if request.method == 'POST':
            if request.POST.get('spots'):
                spot_choices = request.POST.getlist('spots')
            else:
                spot_choices = [spot for spot in Statistics.objects.only('spot').distinct('spot')]
            ## see if 'time choice' can be made its own separate view/function to reduce repitition
            if 'time_choice' in request.POST:
                chosen_time = request.POST.get('time')
                data = read_frame(Statistics.objects.all().filter(time=chosen_time, spot__in=spot_choices))
                plot_div = fx.graph_one_time(data, chosen_time)
            if 'time_range' in request.POST:
                t_from = int(request.POST.get('From'))
                t_to = int(request.POST.get('To'))
                if t_from > t_to:
                    chosen_time = [i for i in range(t_from,24)] + [i for i in range(0, t_to+1)]
                else:
                    chosen_time = [i for i in range(t_from, t_to+1)]
                data = read_frame(Statistics.objects.all().filter(time__in=chosen_time, spot__in=spot_choices))
                plot_div = fx.graph_time_range(data, chosen_time)
            return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
        if 'reset' in request.GET:
            return redirect('probability_charts')
        return render(request, 'parking_spot/combo_form.html', {'form':form})
    
         
    def top_entries(request):
        '''Display entries as table which minimum selected requirements'''
        if request.method == 'POST':
            min_prob, min_entries, max_error = [request.POST.get(choice) for choice in ['min_probability', 'min_entries', 'standard_deviation']]
            min_prob, min_entries, max_error = min_prob or 0.75, min_entries or 0.25, max_error or 0.15

            if 'time_choice' in request.POST:
                chosen_time = request.POST.get('time')
            elif 'time_range' in request.POST:
                t_from = int(request.POST.get('From'))
                t_to = int(request.POST.get('To'))
                if t_from > t_to:
                    chosen_time = [i for i in range(t_from,24)] + [i for i in range(0, t_to+1)]
                else:
                    chosen_time = [i for i in range(t_from, t_to+1)]
            else:
                chosen_time = [i for i in range(0, 24)]
            ## create dynamic table with sort/filter ability.. attempts with django-tables2 and DataTables made unsucesfully 
            table = list(Statistics.objects.all().filter(probability__gte=min_prob, entries__gte=min_entries, std__lte=max_error, time__in=chosen_time).order_by('time','-probability', 'std', '-entries'))
            return render(request, 'parking_spot/stats_table.html', {'stats':table})
        return render(request, 'parking_spot/rec_or_choice_form.html', {'form':TopEntriesForm ,'time_form':TimeForm })




