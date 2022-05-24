from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import sys, os
from plotly.subplots import make_subplots

try:
    from tools import connection as con
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.join(os.path.normpath(sys.path[0]), ".."), "tools"))
    from tools import connection as con

psql = con.ConnectionClient().postgres()

q = '''select * from public.global_crypto_data'''

gcd = pd.read_sql_query(q, con=psql)


def get_volume_plot():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=gcd['timestamp'], y=gcd['total_volume_usd'], name='Total Crypto 24h Market Volume',
                             line=dict(color=' #4265FC', width=4)), secondary_y=False)
    fig.add_trace(go.Scatter(x=gcd['timestamp'], y=gcd['market_cap_usd'], name='Crypto Market Cap',
                             line=dict(color=' #3c3c3d', width=4)), secondary_y=True)
    fig.update_layout(
        plot_bgcolor='white',
        title='Total Volume and Market Cap'
    )
    fig.update_yaxes(title_text="Volume (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Market Cap (USD)", secondary_y=True)
    return fig


app = Dash(__name__)

app.layout = html.Div([
        html.H1(children='Crypto Dashboard'),

        dcc.Graph(
            id='volume',
            figure=get_volume_plot()
        ),

        html.H3(children='Display BTC and ETH Market Cap In: ',
                style={'height': '40px', 'width': '400px', 'margin': 'auto'}),

        html.Div([
            dcc.RadioItems(
                ['Perc', 'USD'],
                'Perc',
                id='yaxis-type',
            )
        ], style={'height': '40px', 'width': '200px', 'margin': 'auto'}),

        dcc.Graph(
            id='market-cap'
        ),
    ]
)


@app.callback(
    Output('market-cap', 'figure'),
    Input('yaxis-type', 'value'))
def get_market_cap_plot(yaxis_type):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=gcd['timestamp'],
                             y=(gcd['btc_market_cap_perc'] if yaxis_type == 'Perc' else gcd['btc_market_cap_perc'] * gcd['market_cap_usd']),
                             name='BTC Market Cap', line=dict(color=' #f2a900', width=4)), secondary_y=False)
    fig.add_trace(go.Scatter(x=gcd['timestamp'],
                             y=(gcd['eth_market_cap_perc'] if yaxis_type == 'Perc' else gcd['eth_market_cap_perc'] * gcd['market_cap_usd']),
                             name='ETH Market Cap', line=dict(color=' #6B8068', width=4)), secondary_y=True)
    fig.update_layout(
        plot_bgcolor='white',
        title='BTC and ETH Market Caps'
    )
    fig.update_yaxes(title_text=f'''BTC Market Cap ({'%' if yaxis_type == 'Perc' else 'USD'})''', secondary_y=False)
    fig.update_yaxes(title_text=f'''ETH Market Cap ({'%' if yaxis_type == 'Perc' else 'USD'})''', secondary_y=True)
    fig.update_yaxes(type='linear' if yaxis_type == 'Perc' else 'log')
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
