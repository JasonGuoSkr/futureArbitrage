# @Time    : 2020/5/18 11:00
# @Author  : GUO LULU

import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.offline import init_notebook_mode,iplot

# data = [go.Scatter(x=Data.index.strftime("%Y-%m-%d %H:%M:%S.%f"), y=Data['IF2004_last'], name='IF'),
#         go.Scatter(x=Data.index.strftime("%Y-%m-%d %H:%M:%S.%f"), y=Data['IH2004_last'], name='IC')]
# data = go.Scatter(x=Data.index.strftime("%Y-%m-%d %H:%M:%S.%f"), y=Data['spread_point'])
# layout = go.Layout(title='金融股价的变化趋势')
# fig = go.Figure(data=data, layout=layout)
# fig.update_layout(xaxis_type="category")
# fig.show()

# fig = make_subplots(specs=[[{"secondary_y": True}]])
# fig.add_trace(
#     go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis data"),
#     secondary_y=False,
# )
#
# fig.add_trace(
#     go.Scatter(x=[2, 3, 4], y=[4, 5, 6], name="yaxis2 data"),
#     secondary_y=True,
# )
#
# # Add figure title
# fig.update_layout(
#     title_text="Double Y Axis Example"
# )
#
# # Set x-axis title
# fig.update_xaxes(title_text="xaxis title")
#
# # Set y-axes titles
# fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
# fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)
#
# fig.show()
