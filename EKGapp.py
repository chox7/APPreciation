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
        dcc.Graph(id='live-update-graph'),
        dcc.Graph(id='breathing-scheme', figure=creating_ramp()),
        dcc.Interval(
            id='interval-component',
            interval=50,  # Aktualizacja co 1 sekundę
            n_intervals=0
        )
    ])

    @app.callback(
        Output('live-update-graph', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_graph_live(n):
        data_buffer = processor.get_data()
        ekg_trace = go.Scatter(
            y=data_buffer,
            mode='lines',
            name='EKG Signal'
        )

        return {
            'data': [ekg_trace],
            'layout': go.Layout(
                title='Live EKG Data',
                #xaxis=dict(), TODO: Dodać czas na osi x
                yaxis=dict(range=[np.min(data_buffer)-200, np.max(data_buffer)+200])  # Dostosuj zakres osi Y do swoich danych
            )
        }
    return app