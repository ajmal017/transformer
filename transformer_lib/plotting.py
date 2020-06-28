import plotly.graph_objects as go

def get_layout( title = '', xaxis = '', yaxis = '', y2axis = '', y3axis = '', yrange =[]):
    return go.Layout(
        title=title,
        xaxis=dict(
            title=xaxis,
            domain=[0.1, 0.8]
        ),
        xaxis2= dict(
            title='xaxis2 title', 
            titlefont=dict(color='rgb(148, 103, 189)'), 
            tickfont=dict(color='rgb(148, 103, 189)'), 
            overlaying='x', 
            side='top' ),
        yaxis=dict(
            title=yaxis,
            range=yrange
        ),
        yaxis2=dict(
            title=y2axis,
            titlefont=dict(
            color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        ),
        yaxis3=dict(
            title=y3axis,
            titlefont=dict(
                color="#d62728"
                ),
            tickfont=dict(
                color="#d62728"
            ),
            overlaying="y",
            side="right",
            position=0.9
        )
    )


def get_layout_3d( title = '',  xaxis = '', yaxis = '', zaxis = '' ):
    return {
        'title':title,
        "scene": 
            {
              "xaxis": {"title": xaxis},
              "yaxis": {"title": yaxis },
              "zaxis": {"title": zaxis }
            }
    }