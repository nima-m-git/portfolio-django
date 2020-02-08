from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from django_pandas.io import read_frame
import pandas as pd

from parking_spot.models import Entries, Statistics
from .forms import EntryForm, TimeForm, SpotForm, TimeRangeForm, spot_choices as spots, ComboForm

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
        if request.method == 'POST':
            form = ComboForm(request.POST)
            if form.is_valid():
                if request.POST.get('spots'):
                    spot_choices = request.POST.getlist('spots')
                else:
                    spot_choices = [spot for spot in Entries.objects.only('spot').distinct('spot')]
                if 'time_choice' in request.POST:
                    chosen_time = request.POST.get('time')
                    # get dataframe from query equivalent 'SELECT SPOT, PROBABILITY, STD, ENTRIES FROM parking_spot_stats WHERE TIME = {}'.format(time))
                    data = read_frame(Statistics.objects.all().filter(time__in=chosen_time, spot__in=spot_choices))
                    data['std'] = data['std']/2
                    fig = px.bar(data, 
                            x='spot', 
                            y='probability', 
                            error_y='std',
                            hover_data=['entries'], 
                            width=1200, height=500,  
                            color='entries', 
                            color_continuous_scale='RdBu',
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
                        xaxis_tickmode='array',
                        xaxis_ticktext = spot_choices,
                        xaxis_tickvals = spot_choices,
                        yaxis_title="Probability",
                        font=dict(
                            family="Courier New, monospace",
                            size=16,
                            color="#000000"
                            ),
                        plot_bgcolor='rgba(0,0,0,0)',
                        )
                    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
                    return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
                if 'time_range' in request.POST:
                    t_from = int(request.POST.get('From'))
                    t_to = int(request.POST.get('To'))
                    if t_from > t_to:
                        time_range = [i for i in range(t_from,24)] + [i for i in range(0, t_to+1)]
                    else:
                        time_range = [i for i in range(t_from, t_to+1)]
                    data = read_frame(Statistics.objects.all().filter(time__in=time_range, spot__in=spot_choices))

                    fig = px.scatter(data,
                        x='time', 
                        y='probability', 
                        hover_name='spot',
                        color='spot',
                        color_continuous_scale='purp',
                        size='entries',
                        hover_data=['entries', 'std'], 
                        width=1200, height=500,
                        error_y='std',  
                        )       
                    fig.update_traces(mode='lines+markers')          
                    fig.update_layout(
                        title={
                            'text':'Spots\' Probabiliy change over Time',
                            'y':1.0,
                            'x':0.5,
                            'font':{
                                'size': 28},
                            },
                        xaxis_title="Time (Hours)",
                        yaxis_title="Probability",
                        font=dict(
                            family="Courier New, monospace",
                            size=16,
                            color="#000000"
                            ),
                        xaxis=dict(
                            tickmode='linear',
                            ticks='outside',
                            tick0=0,
                            dtick=1,
                            range=[t_from-.05, t_to + 0.05]
                            ),
                        yaxis=dict(
                            tickmode='linear',
                            ticks='outside',
                            tick0=0,
                            dtick=0.25,
                            range=[-0.05, 1.05]
                            ),
                        legend=go.layout.Legend(
                            traceorder="normal",
                            bordercolor="Black",
                            borderwidth=1
                            ),
                        plot_bgcolor='rgba(0,0,0,0)',
                        )   
                    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
                    return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
        else:
            form = ComboForm()
        return render(request, 'parking_spot/combo_form.html', {'form':form})
    

    def prob_per_time_visual(request):
        if 'time_choice' in request.GET:
            chosen_time = request.GET.get('time')
            # get dataframe from query equivalent 'SELECT SPOT, PROBABILITY, STD, ENTRIES FROM parking_spot_stats WHERE TIME = {}'.format(time))
            data = read_frame(Statistics.objects.all().filter(time=chosen_time))
            data['std'] = data['std']/2

            fig = px.bar(data, 
                    x='spot', 
                    y='probability', 
                    error_y='std',
                    hover_data=['entries'], 
                    width=1600, height=600,  
                    color='entries', 
                    color_continuous_scale='RdBu',
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
                plot_bgcolor='rgba(0,0,0,0)',
                )
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)
            return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
        if 'time_range' in request.GET:
            t_from = int(request.GET.get('From'))
            t_to = int(request.GET.get('To'))
            if t_from > t_to:
                time_range = [i for i in range(t_from,24)] + [i for i in range(0, t_to+1)]
            else:
                time_range = [i for i in range(t_from, t_to)]
            data = read_frame(Statistics.objects.all().filter(time__in=time_range))

            fig = px.scatter(data,
                x='time', 
                y='probability', 
                hover_name='spot',
                color='spot',
                color_continuous_scale='purp',
                size='entries',
                hover_data=['entries', 'std'], 
                width=1600, height=600,
                error_y='std',  
                )       
            fig.update_traces(mode='lines+markers')          
            fig.update_layout(
                title={
                    'text':'Spots\' Probabiliy change over Time',
                    'y':1.0,
                    'x':0.5,
                    'font':{
                        'size': 28},
                    },
                xaxis_title="Time (Hours)",
                yaxis_title="Probability",
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="#000000"
                    ),
                xaxis=dict(
                    tickmode='linear',
                    ticks='outside',
                    tick0=0,
                    dtick=1,
                    range=[t_from-.05, t_to + 0.05]
                    ),
                yaxis=dict(
                    tickmode='linear',
                    ticks='outside',
                    tick0=0,
                    dtick=0.25,
                    range=[-0.05, 1.05]
                    ),
                legend=go.layout.Legend(
                    traceorder="normal",
                    bordercolor="Black",
                    borderwidth=1
                    ),
                plot_bgcolor='rgba(0,0,0,0)',
                )   
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)
            return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
        return render(request, 'parking_spot/time_form.html', {'form':TimeForm(), 'form2':TimeRangeForm()})
            


    def spots_over_time_visual(request):
        if 'spot_choice' in request.GET:
            spot_choices = request.GET.getlist('spots')
            data = read_frame(Statistics.objects.all().filter(spot__in=spot_choices))
            data['std'] = data['std']/2
            # if singlespot: query = ('SELECT SPOT, PROBABILITY, TIME, STD, ENTRIES FROM parking_spot_statistics WHERE SPOT = (SELECT CAST({} AS VARCHAR))'.format(selected_spots))
            fig = px.scatter(data,
                    x='time', 
                    y='probability', 
                    hover_name='spot',
                    color='spot',
                    color_continuous_scale='purp',
                    size='entries',
                    hover_data=['entries', 'std'], 
                    width=1600, height=600,
                    error_y='std',  
                )       
            fig.update_traces(mode='lines+markers')          
            fig.update_layout(
                title={
                    'text':'Spots\' Probabiliy change over Time',
                    'y':1.0,
                    'x':0.5,
                    'font':{
                        'size': 28},
                    },
                xaxis_title="Time (Hours)",
                yaxis_title="Probability",
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="#000000"
                    ),
                xaxis=dict(
                    tickmode='linear',
                    ticks='outside',
                    tick0=0,
                    dtick=1,
                    range=[-.5,23.5]
                    ),
                yaxis=dict(
                    tickmode='linear',
                    ticks='outside',
                    tick0=0,
                    dtick=0.25,
                    range=[-0.01, 1.01]
                    ),
                legend=go.layout.Legend(
                    traceorder="normal",
                    bordercolor="Black",
                    borderwidth=1
                    ),
                plot_bgcolor='rgba(0,0,0,0)',
                )   
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)
            return render(request, 'parking_spot/graph.html', context={'plot_div': plot_div})
        else:
            return render(request, 'parking_spot/spot_form.html', {'form':SpotForm})
            

    #def recommendation(request):
