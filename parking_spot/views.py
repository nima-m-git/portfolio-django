from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse

from parking_spot.models import Entries, Statistics
from .forms import EntryForm

def index(request):
    return HttpResponse("Parking Spot Index")


def add_entry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        form.save()
        if 'update' in request.POST:
            Stats.update_entries()
        return redirect('add_entry')
    else:
        form = EntryForm()
    spots = Entries.objects.distinct('spot')
    return render(request, 'parking_spot/add_entry.html', {'form': form, 'spots': spots})


def view_entries(request):
    entries = Entries.objects.all().order_by('-date_added')
    return render(request, 'parking_spot/view_entries.html', {'entries':entries})


class Stats():

    def update_entries():
        ''' Deletes 'Statistics' table and repopulates with new Entries '''
        spots = Entries.objects.distinct('spot')
        hours = [str(i).zfill(2) for i in range(24)]
        Statistics.objects.all().delete()
        for spot in spots:
            for hour in hours:
                empty_count = Entries.objects.filter(spot=spot, time=hour, empty=True).count()
                total_count = Entries.objects.filter(spot=spot, time=hour).count()
                if total_count >= 3:
                    probability = empty_count/total_count
                    std = (probability*(1-probability)/total_count)**0.5
                else:
                    probability = None
                    std = None

                Statistics(spot=spot, time=hour, probability=probability, entries=total_count, std=std).save()


    def stats_table(request):
        stats = Statistics.objects.all().order_by('spot', 'time')
        return render(request, 'parking_spot/stats_table.html', {'stats':stats})