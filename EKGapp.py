import dash
from dash import dcc, html 
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from breath import creating_ramp
import numpy as np

def run_dash_app_thread(signal_processor, peaks_detector, hrv_analyzer):
    app = run_dash_app(signal_processor, peaks_detector, hrv_analyzer)
    app.run_server(debug=True, port=8051, use_reloader=False)

def run_dash_app(signal_processor, peaks_detector, hrv_analyzer):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label='Wykresy na żywo', children=[
                html.Button('Start', id='start-button', n_clicks=0),
                html.Button('Stop', id='stop-button', n_clicks=0),
                dcc.Store(id='running-state', data=False),  # Hidden div to store the running state
                html.Div([
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
            ]),
            dcc.Tab(label='Ustawienia sygnałów', children=[
                html.Div([
                    html.Div([
                        html.Label('Sampling Rate'),
                        dcc.Input(id='sampling-rate-input', value=signal_processor.sampling_rate, type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Buffer Size (seconds)'),
                        dcc.Input(id='buffer-size-input', value=5, type='number'),  # Zakładamy domyślną wartość 5 sekund
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                ]),
                html.Div([
                    html.Label('High Pass Filter Parameters'),
                    html.Div([
                        html.Label('Order'),
                        dcc.Input(id='hp-order-input', value=signal_processor.hp_params['order'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Cutoff Frequency (fc)'),
                        dcc.Input(id='hp-fc-input', value=signal_processor.hp_params['fc'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Passband Ripple (rp)'),
                        dcc.Input(id='hp-rp-input', value=signal_processor.hp_params['rp'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Stopband Attenuation (rs)'),
                        dcc.Input(id='hp-rs-input', value=signal_processor.hp_params['rs'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                ]),
                html.Div([
                    html.Label('Low Pass Filter Parameters'),
                    html.Div([
                        html.Label('Order'),
                        dcc.Input(id='lp-order-input', value=signal_processor.lp_params['order'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Cutoff Frequency (fc)'),
                        dcc.Input(id='lp-fc-input', value=signal_processor.lp_params['fc'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Passband Ripple (rp)'),
                        dcc.Input(id='lp-rp-input', value=signal_processor.lp_params.get('rp', ''), type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Stopband Attenuation (rs)'),
                        dcc.Input(id='lp-rs-input', value=signal_processor.lp_params['rs'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                ]),
                html.Div([
                    html.Label('Notch Filter Parameters'),
                    html.Div([
                        html.Label('Frequency (f0)'),
                        dcc.Input(id='notch-f0-input', value=signal_processor.notch_params['f0'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Quality Factor (Q)'),
                        dcc.Input(id='notch-q-input', value=signal_processor.notch_params['Q'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                ]),
                html.Div([
                    html.Label('Peak Detection Settings'),
                    html.Div([
                        html.Label('Prominence'),
                        dcc.Input(id='peak-prominence-input', value=peaks_detector.find_peaks_setting['prominence'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Width'),
                        dcc.Input(id='peak-width-input', value=peaks_detector.find_peaks_setting['width'][0], type='number'),
                        html.Label('to'),
                        dcc.Input(id='peak-width-input-2', value=peaks_detector.find_peaks_setting['width'][1], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Height'),
                        dcc.Input(id='peak-height-input', value=peaks_detector.find_peaks_setting['height'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Distance'),
                        dcc.Input(id='peak-distance-input', value=peaks_detector.find_peaks_setting['distance'], type='number'),
                    ], style={'margin-right': '20px', 'display': 'inline-block'}),
                ]),
                html.Div(id='dummy-output', style={'display': 'none'})
            ]),
            dcc.Tab(label='Informacje', children=[
                html.Div([
                    html.H3('Informacje o aplikacji - APPreciation'),
                    html.P('Aplikacja pomagająca wejść w stan koherencji serca dzięki ćwiczeniom oddechowym.'),
                    html.P('Koherencja serca to stan głębokiego spokoju, w którym rytm serca synchronizuje się z oddechem.'+
                           ' Tętno lekko przyspiesza podczas wdechu i zwalnia podczas wydechu. Pomóc w osiągnięciu tego stanu'+
                            ' może ćwiczenie polegające na wykonywaniu wolnych i spokojnych oddechów. Korzyści z koherencji serca są liczne.'+
                            ' Ciało i umysł regenerują się, poprawiają się pamięć i koncentracja, a także odczuwa się więcej pozytywnych emocji takich jak radość i wdzięczność.'+
                            ' Dodatkowo obniżają się ciśnienie krwi i poziom kortyzolu, co w efekcie zmniejsza poziom stresu.'),
                    html.P(),
                    html.H3('Funkcje'),
                    html.Ul([
                        html.Li('Ćwiczenie oddechowe, które pomoże zsynchronizować oddech z rytmem serca.'),
                        html.Li('Możliwość spersonalizowania długości wdechu i wydechu do indywidualnych potrzeb.'),
                        html.Li('Monitorowanie tętna oraz zmienności rytmu zatokowego.'),
                        html.Li('Wizualizacja poziomu koherencji serca.')
                    ]),
                    html.H3('Przygotowanie badanego'),
                    html.H5('1. Elektrody'),
                    html.P('Potrzebne będą 3 elektrody monopolarne z wtyczką Touch Proof wraz z nalepkami do EKG (rekomendujemy nalepki firmy SKINTACT). '
                        'Poniżej znajdują się zdjęcia referencyjne.'),
                    
                    html.Div(style={'display': 'flex', 'justify-content': 'space-around'}, children=[
                        html.Img(src='/assets/images/1.jpeg', alt='Obrazek 1', style={'width': '25%', 'margin-right': '10px'}),
                        html.Img(src='/assets/images/2.jpeg', alt='Obrazek 2', style={'width': '25%'})
                    ]),
                    
                    html.P('Elektrody należy umieścić na wewnętrznej części obu przedramion (elektrody bipolarne) oraz na wybranej nodze (najlepiej na wewnętrznej stronie, w pobliżu kostki). '
                        'Pamiętaj że przed przyklejeniem nalepki, skórę należy przemyć alkoholem w celu zmniejszenia oporu (odtłuszczenia skóry).'),
                    
                    html.H5('2. Wzmacniacz'),
                    html.P('Potrzebny będzie wzmacniacz Perun firmy BrainTech. Instrukcja obsługi:'),
                    html.A('https://braintech.pl/pliki/svarog/manuals/manual.pdf', href='https://braintech.pl/pliki/svarog/manuals/manual.pdf'),
                    
                    html.Div(style={'display': 'flex', 'justify-content': 'space-around'}, children=[
                        html.Img(src='/assets/images/3.jpeg', alt='Obrazek 3', style={'width': '25%', 'margin-right': '10px'}),
                        html.Img(src='/assets/images/4.jpeg', alt='Obrazek 4', style={'width': '25%'})
                    ]),
                    
                    html.P('Wzmacniacz podłącz do komputera kablem USB - USB B tzw. kabel drukarkowy.'),
                    
                    html.H5('3. Podłączenie elektrod do wzmacniacza'),
                    html.P('Elektrody, które umieszczono na przedramionach, podłącz do portu nr 1 na wzmacniaczu. '
                        'Jedna idzie do czerwonego, a druga do czarnego wejścia (wybór losowy). Elektrodę umieszczoną na nodze '
                        'podłącz do jednego z portów opisanych jako GND (ground). (Porty białe lub żółte).')
                ])
            ])
        ])
    ])

    @app.callback(
        Output('running-state', 'data'),
        [Input('start-button', 'n_clicks'),
         Input('stop-button', 'n_clicks')],
        [State('running-state', 'data')]
    )
    def update_running_state(start_clicks, stop_clicks, running_state):
        ctx = dash.callback_context

        if not ctx.triggered:
            return running_state

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'start-button':
            signal_processor.start()
            peaks_detector.start()
            hrv_analyzer.start()
            return True
        elif button_id == 'stop-button':
            signal_processor.stop()
            peaks_detector.stop()
            hrv_analyzer.stop()
            return False
    
    @app.callback(
        Output('live-graph-ekg', 'figure'),
        Input('interval-component', 'n_intervals'),
        State('running-state', 'data')
    )
    def update_EKG_plot(n, running_state):
        if not running_state:
            return dash.no_update

        data_buffer, time_buffer = signal_processor.get_data()

        ekg_trace = go.Scatter(
            x=time_buffer,
            y=data_buffer,
            mode='lines',
            name=f'EKG Signal',
        )
        
        # peaks, prominences = peaks_detector.get_peaks()
        # shapes = []
        # for peak, prominence in zip(peaks, prominences):
        #    shapes.append(
        #        dict(
        #            type="line",
        #            x0=peak, y0=0,#data_buffer[int((peak - time_buffer[0])*processor.sampling_rate)] - prominence,
        #            x1=peak, y1=2000,#data_buffer[int((peak - time_buffer[0])*processor.sampling_rate)],
        #            line=dict(color="red", width=3)
        #        )
        #    )
        
        return {
            'data': [ekg_trace],
            'layout': go.Layout(
                title=f'Live EKG Data',
                #shapes=shapes,
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
    
    @app.callback(
        Output('live-graph-hr', 'figure'),
        Input('interval-component', 'n_intervals'),
        State('running-state', 'data')
    )
    def update_HR_plot(n, running_state):
        if not running_state:
            return dash.no_update

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
    

    @app.callback(
        Output('live-graph-hrv', 'figure'),
        Input('interval-component', 'n_intervals'),
        State('running-state', 'data')
    )
    def update_HRV_plot(n, running_state):
        if not running_state:
            return dash.no_update
        
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

    @app.callback(
        Output('live-graph-coherence', 'figure'),
        Input('interval-component', 'n_intervals'),
        State('running-state', 'data')
    )
    def update_coherence_plot(n, running_state):
        if not running_state:
            return dash.no_update
        
        x, coh = hrv_analyzer.get_coherence()

        if np.array_equal(coh, np.array(None)) :
            coh = np.zeros(len(x))

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
    
    @app.callback(
        Output('dummy-output', 'children'),
        [
            Input('sampling-rate-input', 'value'),
            Input('buffer-size-input', 'value'),
            Input('hp-order-input', 'value'),
            Input('hp-fc-input', 'value'),
            Input('hp-rp-input', 'value'),
            Input('hp-rs-input', 'value'),
            Input('lp-order-input', 'value'),
            Input('lp-fc-input', 'value'),
            Input('lp-rp-input', 'value'),
            Input('lp-rs-input', 'value'),
            Input('notch-f0-input', 'value'),
            Input('notch-q-input', 'value'),
            Input('peak-prominence-input', 'value'),
            Input('peak-width-input', 'value'),
            Input('peak-width-input-2', 'value'),
            Input('peak-height-input', 'value'),
            Input('peak-distance-input', 'value')
        ]
    )
    def update_settings(
            sampling_rate, buffer_size_seconds,
            hp_order, hp_fc, hp_rp, hp_rs,
            lp_order, lp_fc, lp_rp, lp_rs,
            notch_f0, notch_q,
            peak_prominence, peak_width, peak_width_2, peak_height, peak_distance,
    ):
        signal_processor.sampling_rate = sampling_rate
        signal_processor.buffor_size = sampling_rate * buffer_size_seconds
        signal_processor.hp_params = {'order': hp_order, 'fc': hp_fc, 'rp': hp_rp, 'rs': hp_rs}
        signal_processor.lp_params = {'order': lp_order, 'fc': lp_fc, 'rp': lp_rp, 'rs': lp_rs}
        signal_processor.notch_params = {'f0': notch_f0, 'Q': notch_q}
        
        peaks_detector.find_peaks_setting = {
            'prominence': peak_prominence,
            'width': [peak_width, peak_width_2],
            'height': peak_height,
            'distance': peak_distance
        }
        return ''

    return app
