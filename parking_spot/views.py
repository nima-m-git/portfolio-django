from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from django_pandas.io import read_frame

from parking_spot.models import Entries, Statistics
from .forms import EntryForm, TimeForm

def index(request):
    return render(request, 'parking_spot/index.html')


def add_entry(request):
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
    entries = Entries.objects.all().order_by('-date_added')
    return render(request, 'parking_spot/view_entries.html', {'entries':entries})


class Stats():


    def index(request):
        return render(request, 'parking_spot/stats_index.html')


    def update_entries():
        ''' Deletes 'Statistics' table and repopulates with new Entries '''
        spots = Entries.objects.distinct('spot')
        hours = [str(i).zfill(2) for i in range(24)]
        min_entries = 3
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

    
    def prob_per_time_visual(request):
        if 'time_choice' in request.GET:
            #show visual
            chosen_time = request.GET.get('time')
            # get dataframe from query equivalent
            #('SELECT SPOT, PROBABILITY, STD, ENTRIES FROM parking_spot_stats WHERE TIME = {}'.format(time))
            data = read_frame(Statistics.objects.all().filter(time=chosen_time))

            fig = px.bar(data, x='spot', y='probability', error_y='std',
                    hover_data=['entries'], width=1600, height=800,  
                    #color='probability', 
                    #color_continuous_scale='purp',
                    #plot_bgcolor='rgba(0,0,0,0)', 
                    # NOT WORKING -- FIX!
                )
        
            fig.update_layout(
                title={
                    'text':'{}Hs'.format(chosen_time),
                    'y':1.0,
                    'x':0.5,
                    'font':{
                        'size': 28},
                    },
                xaxis_title="Spot",
                xaxis_tickmode='linear',
                yaxis_title="Probability",
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="#000000"
                    ),
                )
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)
            return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
        else:
            return render(request, 'parking_spot/time_form.html', {'form':TimeForm()})


