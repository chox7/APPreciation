import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def creating_ramp(hold_zero = 15 , inhale = 10, hold_one = 15, exhale = 10, speed = 2, info_from_user = True, text_above_dot = False):

    # scheme settings can be set in function or by the user
    if info_from_user:
        hold_zero = int(input("Enter the 'hold_zero' time: "))
        inhale = int(input("Enter the 'inhale' time: "))
        hold_one = int(input("Enter the 'hold_one' time: "))
        exhale = int(input("Enter the 'exhale' time: "))
        speed = int(input("How fast should the exercise be? [0 - very slow, 1 - slow, medium, 2 - fast, 3 - very fast]. Enter the chosen --speed number-- :" ))

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


    # if it's chosen, the command will be shown above the animated dot
    if text_above_dot:
        mode_pick = "markers + text"
    else:
        mode_pick = "markers"

    # commandtext visiuals
    def instruct(n):
            if hold_zero < n%(hold_zero + inhale + hold_one + exhale) <= hold_zero + inhale:
                return ['middle left','inhale']
            elif hold_zero + inhale + hold_one < n%(hold_zero + inhale + hold_one + exhale) <= hold_zero + inhale + hold_one + exhale:
                return ['middle right', 'exhale']
            else:
                return ['top center','hold']


    #examples, can be changed
    speedrange = [300, 200, 100, 50, 20, 10]

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
                            args=[None, {"frame": {"duration": speedrange[speed],  
                                                    'easing': 'linear', #still working on the easing
                                                    "redraw": True},
                                                    "fromcurrent": True, 
                                                    "transition": {"duration": 0}}]),
                        dict(label="pause",
                            method = "animate",
                            args=[[None], {'mode' :  "immediate"}])]))]
    ),
    frames= [go.Frame(data=[go.Scatter(x=[i], y=[n], mode = mode_pick,  textposition = instruct(i)[0]
                            ,texttemplate = instruct(i)[1])]) for i, n in enumerate(scheme)])
    fig.add_trace(go.Line(
        x=df["index"],
        y=df["value"],
        line_color = '#003366'
       ))

    #not showing ticks,grids and some visual optional changes

    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(showlegend= False, 
                    template='presentation', #for now i think the blue color for all the texts look nice, but we have the opition to change eg. title features
                    #title_font_color = 'black',
                    #title_font_family="Overpass",
                    font_family="Courier New",
                    font_color="#003399")
    fig.update_traces(marker=dict(size=20, symbol= 'circle', color=["#6699CC"]))
    return fig

if _name_ == ”__main__”:
    scheme = creating_ramp()
    scheme.show()


