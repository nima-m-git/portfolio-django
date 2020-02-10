import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot

from parking_spot.forms import TimeForm


def graph_one_time(data, chosen_time):
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
        xaxis_ticktext = data['spot'],
        xaxis_tickvals = data['spot'],
        yaxis_title="Probability",
        font=dict(
            family="Courier New, monospace",
            size=16,
            color="#000000"
            ),
        plot_bgcolor='rgba(0,0,0,0)',
        )
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div
     

def graph_time_range(data, chosen_time):
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
    #fig.update_traces(mode='lines+markers')     
    # not working well with category time not in numeric order     
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
            type='category',
            tickmode='array',
            categoryorder='array',
            categoryarray=chosen_time,
            ticks='outside',
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
    return plot_div

def choose_time(request):
    form = TimeForm
    if request.method == 'POST':
        if 'time_choice' in request.POST:
            chosen_time = request.POST.get('time')
        if 'time_range' in request.POST:
            t_from = int(request.POST.get('From'))
            t_to = int(request.POST.get('To'))
            if t_from > t_to:
                chosen_time = [i for i in range(t_from,24)] + [i for i in range(0, t_to+1)]
            else:
                chosen_time = [i for i in range(t_from, t_to+1)]
        return chosen_time
    return render(request, 'parking_spot/time_form.html', {'form': form})

def which_graph(data, time_choice, t_from='', t_to=''):
        if len(time_choice) == 1:
            return graph_one_time(data)
        elif len(time_choice) > 1:
            return graph_time_range(data, t_from, t_to)
