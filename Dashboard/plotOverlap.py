import plotly.graph_objects as go
import numpy as np

if __name__ == '__main__':
    x = ["10-99", "100-999", "1000-9999", "10000-99999"]
    overlap = [0.0125, 0.00625, 0.003125, 0.0015875]

    fig = go.Figure(data=[
        go.Bar(name='Initial upper limit <br> for the lower partition', x=x, y=np.full((1, 4), 0.01)[0]),
        go.Bar(name='Overlap range into <br> the middle partition', x=x, y=overlap)
    ])

    fig.update_layout(barmode='stack', xaxis_title="Number of Items", yaxis_title="Range of Lower Partition")
    fig.show()