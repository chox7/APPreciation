import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def creating_ramp(hold_zero=15, inhale=10, hold_one=15, exhale=10, speed=-3, loops=10, info_from_user=False, text_above_dot=True):

    # Scheme settings can be set in function or by the user
    if info_from_user:
        hold_zero = int(input("Enter the 'hold_zero' time: "))
        inhale = int(input("Enter the 'inhale' time: "))
        hold_one = int(input("Enter the 'hold_one' time: "))
        exhale = int(input("Enter the 'exhale' time: "))
        speed = int(input("How fast should the exercise be? [0 - very slow, 1 - slow, medium, 2 - fast, 3 - very fast]. Enter the chosen --speed number-- :"))

    # One segment
    sig = np.concatenate((np.zeros(hold_zero // 2),
                          np.arange(0, 1, 1 / inhale),
                          np.ones(hold_one),
                          np.arange(1, 0, -1 / exhale),
                          np.zeros(hold_zero // 2)))

    # Just visual, the length can be changed
    scheme = np.tile(sig, 3)
    loop_time = len(sig)
    total_time = len(scheme)
    index = np.arange(0, total_time, 1)

    # Data
    d = {'index': index, 'value': scheme}
    df = pd.DataFrame(data=d)

    # If it's chosen, the command will be shown above the animated dot
    if text_above_dot:
        mode_pick = "markers+text"
    else:
        mode_pick = "markers"

    # Command text visuals
    def instruct(n):
        segment_time = hold_zero//2 + inhale + hold_one + exhale + hold_zero//2
        pos = n % segment_time
        if pos < hold_zero // 2:
            return ['top center', 'hold']
        elif pos < hold_zero // 2 + inhale:
            return ['middle left', 'inhale']
        elif pos < hold_zero // 2 + inhale + hold_one:
            return ['top center', 'hold']
        elif pos < hold_zero // 2 + inhale + hold_one + exhale:
            return ['middle right', 'exhale']
        else:
            return ['top center', 'hold']

    # Examples, can be changed
    speedrange = [100, 50, 25, 15, 10, 5]

    # Interpolate additional frames for smooth animation
    interpolation_factor = 5  # Number of intermediate frames to add between each main frame
    extended_scheme = np.interp(np.arange(0, total_time, 1 / interpolation_factor), np.arange(0, total_time), scheme)

    # Create frames for animation
    frames = [go.Frame(data=[go.Scatter(x=[(i / interpolation_factor) % total_time], y=[n], mode=mode_pick,
                                        textposition=instruct(int(i / interpolation_factor) % loop_time)[0],
                                        texttemplate=instruct(int(i / interpolation_factor) % loop_time)[1])])
              for i, n in enumerate(np.tile(extended_scheme,3))]


    # Animated dot following the scheme activated by the button
    fig = go.Figure(
        data=[go.Scatter(x=[0], y=[0])],  # Starting point
        layout=go.Layout(
            xaxis=dict(range=[0, total_time], autorange=False),  # Set x-axis range based on original scheme length
            yaxis=dict(range=[-0.25, 1.25], autorange=False),
            title=" -- Breathing Scheme --",
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=list([
                        dict(label="start",
                             method="animate",
                             args=[None, {"frame": {"duration": speedrange[speed],
                                                    "redraw": True},
                                          "fromcurrent": True,
                                          "mode": "immediate",
                                          "transition": {"duration": 0}}]),
                        dict(label="pause",
                             method="animate",
                             args=[[None], {'mode': "immediate"}])]))]
        ),
        frames=frames
    )

    fig.add_trace(go.Scatter(
        x=df["index"],
        y=df["value"],
        line_color='#003366'
    ))

    # Not showing ticks, grids and some visual optional changes
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(showlegend=False,
                      template='presentation',
                      font_family="Courier New",
                      font_color="#003399")
    fig.update_traces(marker=dict(size=20, symbol='circle', color=["#6699CC"]))
    return fig

if __name__ == '__main__':
    scheme = creating_ramp()
    scheme.show()


