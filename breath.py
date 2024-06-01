import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

#this function creates a desired breathing scheme

def creating_ramp(hold_zero= 10 , inhale=9, hold_one=7, exhale=8):

    #one segment
    sig = np.concatenate((np.zeros(hold_zero), 
                        np.arange(0, 1, 1/inhale), 
                        np.ones(hold_one), 
                        np.arange(1, 0, -1/exhale)))

    #just visual, the length can be changed
    scheme = np.concatenate((sig, sig, np.zeros(hold_zero)))
    index = np.arange(0, len(scheme), 1)

    #data
    d = {'index': index, 'value': scheme}
    df = pd.DataFrame(data=d)

    #animated dot following the scheme activated by the button
    fig = go.Figure(
    data=[go.Scatter(x=[0], y=[0])], #starting point
    layout=go.Layout(
        xaxis=dict(range=[0, len(scheme)], autorange=False),
        yaxis=dict(range=[-0.25, 1.25], autorange=False),
        title=" -- Breathing Scheme --",
        updatemenus=[
            dict(
                type="buttons",
                buttons = list([
                        dict(label="start",
                            method="animate",
                            args=[None]),
                        dict(label="pause",
                            method = "animate",
                            args=[[None], {'mode' :  "immediate"}])]))]
    ),
    frames= [go.Frame(data=[go.Scatter(x=[i], y=[n])]) for i, n in enumerate(scheme)])
    fig.add_trace(go.Line(
        x=df["index"],
        y=df["value"],
        line_color = '#003366'
       ))

    #not showing ticks,grids and some visual optional changes

    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(showlegend= False, 
                    template='presentation', 
                    #title_font_color = 'black',
                    #title_font_family="Overpass",
                    font_family="Courier New",
                    font_color="#003399")
    fig.update_traces(marker=dict(size=20, symbol= 'circle', color=["#6699CC"]))

    return fig

scheme = creating_ramp()
scheme.show()



