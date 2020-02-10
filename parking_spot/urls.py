from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_entry', views.add_entry, name='add_entry'),
    path('view_entries', views.view_entries, name='view_entries'),
    path('stats_table', views.Stats.stats_table, name='stats_table'),
    path('stats', views.Stats.index, name='stats_index'),
    path('stats/probability_charts', views.Stats.probability_charts, name='probability_charts'),
    path('stats/top_entries', views.Stats.top_entries, name='top_entries'),
]

