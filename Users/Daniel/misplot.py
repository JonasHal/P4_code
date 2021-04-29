import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv(Path('../../Data/MS-Apriori_FP_sets.csv'), sep=',')

# plt.plot(df['MIS_threshold'], df['Execution_time'])
# plt.show()

#fig = px.line(df, x='MIS_threshold', y='Execution_time')
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.MIS_threshold, y=df.Total_FP_sets, mode='lines'))
fig.add_trace(go.Scatter(x=df.MIS_threshold, y=df.Total_FP_sets, mode='markers', marker=dict(color='red', size=10)))
fig.update_layout(title='', xaxis_title='MIS Threshold', yaxis_title='Frequent property sets', showlegend=False)
fig.write_image('fp_sets_mis.png')
fig.write_html('fp_sets_mis.html')
#fig.show()