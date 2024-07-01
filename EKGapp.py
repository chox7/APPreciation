import dash
from dash import dcc, html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from breath import creating_ramp
import numpy as np
import lsl_perun32 as lsl


def add_data_continuously(inlet, samps_per_chunk, signal_processor):
    while True:
        try:
            sample, timestamp = inlet.pull_chunk(timeout=1.0, max_samples=samps_per_chunk)
            piece = np.array(sample)
            piece = piece[:, 23]
            signal_processor.add_data(piece)
        except StopIteration:
            break    

def run_dash_app_thread(signal_processor, peaks_detector, hrv_analyzer):
    app = run_dash_app(signal_processor, peaks_detector, hrv_analyzer)
    app.run_server(debug=True, port=8051, use_reloader=False)

def run_dash_app(signal_processor, peaks_detector, hrv_analyzer):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(id='live-graph-ekg', style={'width': '25%', 'display': 'inline-block'}),
        dcc.Graph(id='live-graph-hr', style={'width': '25%', 'display': 'inline-block'}),
        dcc.Graph(id='live-graph-hrv', style={'width': '25%', 'display': 'inline-block'}),
        dcc.Graph(id='live-graph-coherence', style={'width': '25%', 'display': 'inline-block'}),
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
        data_buffer, time_buffer = signal_processor.get_data()

        ekg_trace = go.Scatter(
            x=time_buffer,
            y=data_buffer,
            mode='lines',
            name=f'EKG Signal',
        )
        
        peaks, prominences = peaks_detector.get_peaks()
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
        bpm = peaks_detector.get_bpm()
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
                    range=[20,200]  # Zakres tętna w BPM (dostosuj do potrzeb)
                )
            )
        }
    

    @app.callback(Output('live-graph-hrv', 'figure'),
              Input('interval-component', 'n_intervals'))
    def update_HRV_plot(n):
        F = hrv_analyzer.get_frequencies()
        P = hrv_analyzer.get_power()

        if np.array_equal(F, np.array(None)) or np.array_equal(P, np.array(None)):
            F = np.zeros(100)
            P = np.linspace(0,1,100)
        
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
                    range = [0,0.55]  # Zakres osi częstotliwości
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='black',  # Linia osi Y w kolorze czarnym
                    #range=[0,300]  # Zakres osi mocy
                )
            )
        }

    @app.callback(Output('live-graph-coherence', 'figure'),
              Input('interval-component', 'n_intervals'))
    def update_coherence_plot(n):
        x, coh = hrv_analyzer.get_coherence()
        coherence_trace = go.Scatter(
            x=x,
            y=coh,
            mode='lines',
            name='Coherence'
        )
        
        return {
            'data': [coherence_trace],
            'layout': go.Layout(
                title='Coherence',
                plot_bgcolor='white',  # Białe tło wykresu
                paper_bgcolor='white',  # Białe tło papieru
                xaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='lightgray',
                    range = [-4,4],  # Zakres osi częstotliwości
                    showticklabels=False
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  # Siatka w kolorze jasnoszarym
                    linecolor='lightgray',  # Linia osi Y w kolorze czarnym
                    range=[0,1]  # Zakres osi mocy
                )
            )
        }
    return app