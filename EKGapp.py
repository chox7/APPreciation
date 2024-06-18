import dash
from dash import dcc, html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from breath import creating_ramp
import numpy as np
import lsl_perun32 as lsl


def add_data_continuously(HR, data, filts):
    '''
    Chunk filtered posiada np.array o kształcie: (processing_chunk_size, liczba_kanałów=32)
    Jest już przefiltrowany
    lsl.simulate_aqusition zwraca generator, za każdym razem jak zadziałasz na niego funkcją next(), dostaniesz kolejny
    chunk danych
    '''
    while True:
        try:
            piece = next(data)
            chunk_filtered = lsl.filter_chunk(piece, filts)
            HR.add_data(chunk_filtered)
        except StopIteration:
            break    

def run_dash_app(processor):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(id='live-graph-ekg', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='live-graph-hr', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='live-graph-hrv', style={'width': '33%', 'display': 'inline-block'}),
        dcc.Graph(id='breathing-scheme', figure=creating_ramp(info_from_user = False)),
        dcc.Interval(
            id='interval-component',
            interval=50,  # Aktualizacja co 50 ms
            n_intervals=0
        )
    ])

    @app.callback(
        Output('live-graph-ekg', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_EKG_plot(n):
        data_buffer, time_buffer = processor.get_data()

        ekg_trace = go.Scatter(
            x=time_buffer,
            y=data_buffer,
            mode='lines',
            name=f'EKG Signal',
        )
        
        peaks, prominences = processor.get_peaks()
        shapes = []
        for peak, prominence in zip(peaks, prominences):
            shapes.append(
                dict(
                    type="line",
                    x0=peak, y0=-200,#data_buffer[int((peak - time_buffer[0])*processor.sampling_rate)] - prominence,
                    x1=peak, y1=200,#data_buffer[int((peak - time_buffer[0])*processor.sampling_rate)],
                    line=dict(color="orange", width=2)
                )
            )
        

        return {
            'data': [ekg_trace],
            'layout': go.Layout(
                title=f'Live EKG Data',
                shapes=shapes,
                plot_bgcolor='white',  # Białe tło wykresu
                paper_bgcolor='white',  # Białe tło papieru
                xaxis=dict(
                    gridcolor='white',  # Siatka w kolorze jasnoszarym
                    linecolor='white',  # Linia osi X w kolorze czarnym
                    range=[time_buffer[0], time_buffer[-1]]
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='black',  # Linia osi Y w kolorze czarnym
                    range=[1.2 * np.min(data_buffer), 1.2 * np.max(data_buffer)]
                )
            )
        }
    
    @app.callback(Output('live-graph-hr', 'figure'),
              Input('interval-component', 'n_intervals'))
    def update_HR_plot(n):
        bpm = processor.get_bpm()
        hr_trace = go.Scatter(
            y=bpm,
            mode='lines',
            name='Heart Rate'
        )
        
        return {
            'data': [hr_trace],
            'layout': go.Layout(
                title='Live Heart Rate',
                plot_bgcolor='white',  # Białe tło wykresu
                paper_bgcolor='white',  # Białe tło papieru
                xaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='black'  # Linia osi X w kolorze czarnym
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='black',  # Linia osi Y w kolorze czarnym
                    range=[20,300]  # Zakres tętna w BPM (dostosuj do potrzeb)
                )
            )
        }
    

    @app.callback(Output('live-graph-hrv', 'figure'),
              Input('interval-component', 'n_intervals'))
    def update_HRV_plot(n):
        P = processor.get_frequencies()
        F = processor.get_power()
        hrv_trace = go.Scatter(
            x=F,
            y=P,
            mode='lines',
            name='Heart Rate Variability'
        )
        
        return {
            'data': [hrv_trace],
            'layout': go.Layout(
                title='Live Heart Rate Variability',
                plot_bgcolor='white',  # Białe tło wykresu
                paper_bgcolor='white',  # Białe tło papieru
                xaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='black',
                    range = [0,0.5]  # Zakres osi częstotliwości
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='black',  # Linia osi Y w kolorze czarnym
                    range=[0,300]  # Zakres osi mocy
                )
            )
        }
    return app