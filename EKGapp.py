import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from breath import creating_ramp
import numpy as np

chart_settings = {
    'ekg': {
        'range': [-500, 2000],
    },
    'hr': {
        'range': [20, 200],
    }
}

# Function to run the Dash app
def run_dash_app_thread(signal_processor, peaks_detector, hrv_analyzer, interval, **breathing_settings):
    app = run_dash_app(signal_processor, peaks_detector, hrv_analyzer, interval, **breathing_settings)
    app.run_server(debug=True, port=8051, use_reloader=False)

# Function to create the Dash app
def run_dash_app(signal_processor, peaks_detector, hrv_analyzer, interval_value=1000, **breathing_settings):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label='Live Charts', children=[
                html.Button('Start', id='start-button', n_clicks=0),
                html.Button('Stop', id='stop-button', n_clicks=0),
                dcc.Store(id='running-state', data=False),
                html.Div([
                    dcc.Graph(id='live-graph-ekg', style={'width': '25%', 'display': 'inline-block'}),
                    dcc.Graph(id='live-graph-hr', style={'width': '25%', 'display': 'inline-block'}),
                    dcc.Graph(id='live-graph-hrv', style={'width': '25%', 'display': 'inline-block'}),
                    dcc.Graph(id='live-graph-coherence', style={'width': '25%', 'display': 'inline-block'}),
                    dcc.Graph(id='breathing-scheme', figure=creating_ramp(**breathing_settings, info_from_user = False)),
                    dcc.Interval(
                        id='interval-component',
                        interval= interval_value,  # in milliseconds
                        n_intervals=0
                    )
                ])
            ]),
            dcc.Tab(label='Settings ', children=[
                # Signal settings group
                html.Fieldset([
                    html.Legend('General Settings'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Sampling Rate (Hz):'),
                            dbc.Input(id='sampling-rate-input', value=signal_processor.sampling_rate, type='number')
                        ], width=6),
                        dbc.Col([
                            dbc.Label('Show Peaks:'),
                            dcc.Checklist(
                                options=[{'label': '', 'value': 'show_peaks'}],
                                id='show-peaks-toggle',
                                value=[]  # Default to unchecked
                            )
                        ], width=6),
                    ]),
                ], className='filter-group'),
            
                # Chart view settings
                html.Fieldset([
                    html.Legend('Chart Settings'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('EKG chart y-axis range:'),
                            dbc.Input(id='ekg-range-1', value=chart_settings['ekg']['range'][0], type='number'),
                            dbc.Label('to'),
                            dbc.Input(id='ekg-range-2', value=chart_settings['ekg']['range'][1], type='number'),
                        ], width=6),
                        dbc.Col([
                            dbc.Label('HR chart y-axis range:'),
                            dbc.Input(id='hr-range-1', value=chart_settings['hr']['range'][0], type='number'),
                            dbc.Label('to'),
                            dbc.Input(id='hr-range-2', value=chart_settings['hr']['range'][1], type='number'),
                        ], width=6),
                    ]),
                ], className='filter-group'),

                # High Pass Filter group
                html.Fieldset([
                    html.Legend('High Pass Filter Parameters '),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Order: '),
                            dbc.Input(id='hp-order-input', value=signal_processor.hp_params['order'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Cutoff Frequency (fc): '),
                            dbc.Input(id='hp-fc-input', value=signal_processor.hp_params['fc'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Passband Ripple (rp): '),
                            dbc.Input(id='hp-rp-input', value=signal_processor.hp_params['rp'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Stopband Attenuation (rs): '),
                            dbc.Input(id='hp-rs-input', value=signal_processor.hp_params['rs'], type='number')
                        ], width=3),
                    ], className='mb-3')
                ], className='filter-group'),

                # Low Pass Filter group
                html.Fieldset([
                    html.Legend('Low Pass Filter Parameters: '),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Order: '),
                            dbc.Input(id='lp-order-input', value=signal_processor.lp_params['order'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Cutoff Frequency (fc): '),
                            dbc.Input(id='lp-fc-input', value=signal_processor.lp_params['fc'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Passband Ripple (rp): '),
                            dbc.Input(id='lp-rp-input', value=signal_processor.lp_params['rp'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Stopband Attenuation (rs): '),
                            dbc.Input(id='lp-rs-input', value=signal_processor.lp_params['rs'], type='number')
                        ], width=3),
                    ], className='mb-3')
                ], className='filter-group'),

                # Notch Filter group
                html.Fieldset([
                    html.Legend('Notch Filter Parameters '),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Frequency (f0): '),
                            dbc.Input(id='notch-f0-input', value=signal_processor.notch_params['f0'], type='number')
                        ], width=6),
                        dbc.Col([
                            dbc.Label('Quality Factor (Q): '),
                            dbc.Input(id='notch-q-input', value=signal_processor.notch_params['Q'], type='number')
                        ], width=6),
                    ], className='mb-3')
                ], className='filter-group'),

                # Peak Detection group
                html.Fieldset([
                    html.Legend('Peak Detection Settings '),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Prominence: '),
                            dbc.Input(id='peak-prominence-input', value=peaks_detector.find_peaks_setting['prominence'], type='number')
                        ], width=3),
                        dbc.Col([
                            dbc.Label('Width range: '),
                            dbc.Input(id='peak-width-input', value=peaks_detector.find_peaks_setting['width'][0], type='number'),
                            dbc.Label(' to '),
                            dbc.Input(id='peak-width-input-2', value=peaks_detector.find_peaks_setting['width'][1], type='number')
                        ], width=1),
                        dbc.Col([
                            dbc.Label('Height: '),
                            dbc.Input(id='peak-height-input', value=peaks_detector.find_peaks_setting['height'], type='number')
                        ], width=2),
                        dbc.Col([
                            dbc.Label('Distance: '),
                            dbc.Input(id='peak-distance-input', value=peaks_detector.find_peaks_setting['distance'], type='number')
                        ], width=3),
                    ], className='mb-3')
                ], className='filter-group'),

                html.Div(id='dummy-output', style={'display': 'none'})
            ]),
            dcc.Tab(label='About the App ', children=[
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
        State('running-state', 'data'),
        Input('show-peaks-toggle', 'value'),
    )
    def update_EKG_plot(n, running_state, show_peaks):
        if not running_state:
            return dash.no_update

        data_buffer, time_buffer = signal_processor.get_data()

        ekg_trace = go.Scatter(
            x=time_buffer,
            y=data_buffer,
            mode='lines',
            name=f'EKG Signal',
        )

        shapes = []
        if 'show_peaks' in show_peaks:
            peaks, prominences = peaks_detector.get_peaks()
            for peak, prominence in zip(peaks, prominences):
                shapes.append(
                    dict(
                        type="line",
                        x0=peak, y0=0,#data_buffer[int((peak - time_buffer[0])*processor.sampling_rate)] - prominence,
                        x1=peak, y1=2000,#data_buffer[int((peak - time_buffer[0])*processor.sampling_rate)],
                        line=dict(color="red", width=3)
                    )
            )
        
        return {
            'data': [ekg_trace],
            'layout': go.Layout(
                title=f'Live EKG Data',
                shapes=shapes,    
                plot_bgcolor='white', 
                paper_bgcolor='white',  
                xaxis=dict(
                    gridcolor='white',  
                    linecolor='white',  
                    range=[time_buffer[0], time_buffer[-1]]
                ),
                yaxis=dict(
                    gridcolor='lightgrey', 
                    linecolor='black',
                    range=[chart_settings['ekg']['range'][0], chart_settings['ekg']['range'][1]]
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
                plot_bgcolor='white',  
                paper_bgcolor='white',  
                xaxis=dict(
                    gridcolor='lightgrey',  
                    linecolor='black'  
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  
                    linecolor='black', 
                    range=[chart_settings['hr']['range'][0], chart_settings['hr']['range'][1]]
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
        
        F = F[::10]
        P = P[::10]
        
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
                plot_bgcolor='white',  
                paper_bgcolor='white', 
                xaxis=dict(
                    gridcolor='lightgrey', 
                    linecolor='black',
                    range = [0,0.55]  # Range of frequencies
                ),
                yaxis=dict(
                    gridcolor='lightgrey', 
                    linecolor='black', 
                    #range=[0,300] 
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
        
        x = x[::10]
        coh = coh[::10]

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
                plot_bgcolor='white',
                paper_bgcolor='white',  
                xaxis=dict(
                    gridcolor='lightgrey',  
                    linecolor='lightgray',
                    range = [-4,4],  
                    showticklabels=False
                ),
                yaxis=dict(
                    gridcolor='lightgrey',  
                    linecolor='lightgray',  
                    range=[0,1]  
                )
            )
        }
    
    @app.callback(
        Output('dummy-output', 'children'),
        [Input('sampling-rate-input', 'value'),
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
        Input('peak-distance-input', 'value')]
    )
    def save_settings(
            sampling_rate,
            hp_order, hp_fc, hp_rp, hp_rs,
            lp_order, lp_fc, lp_rp, lp_rs,
            notch_f0, notch_q,
            peak_prominence, peak_width, peak_width_2, peak_height, peak_distance,
    ):  
        print('Settings saved.')
        signal_processor.sampling_rate = sampling_rate
        signal_processor.hp_params = {'order': hp_order, 'fc': hp_fc, 'rp': hp_rp, 'rs': hp_rs}
        signal_processor.lp_params = {'order': lp_order, 'fc': lp_fc, 'rp': lp_rp, 'rs': lp_rs}
        signal_processor.notch_params = {'f0': notch_f0, 'Q': notch_q}
        signal_processor.update_filters()
        
        peaks_detector.find_peaks_setting = {
            'prominence': peak_prominence,
            'width': [peak_width, peak_width_2],
            'height': peak_height,
            'distance': peak_distance
        }
        
        return ''

    return app
