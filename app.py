from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import sys, os
from plotly.subplots import make_subplots

try:
    from tools import connection as con
    from tools.market_data.ftx_market_data import GetFTXData
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.join(os.path.normpath(sys.path[0]), ".."), "tools"))
    from tools import connection as con
    from tools.market_data.ftx_market_data import GetFTXData

psql = con.ConnectionClient().postgres()

q = '''select * from public.global_crypto_data'''

gcd = pd.read_sql_query(q, con=psql)


app = Dash(__name__, title='Crypto Dashboard')

app.layout = html.Div([
        html.H1(children='Crypto Dashboard',
                style={'text-align': 'center', 'font-family': 'Helvetica'}),

        html.Div([
            html.Div([
                dcc.RadioItems(
                    ['USD', 'BTC'],
                    'USD',
                    id='yaxis-type-volume',
                    inline=True
                )
                ], style={'width': '48%', 'display': 'inline-block'}
            ),
            html.Div([
                dcc.RadioItems(
                    ['Perc', 'USD'],
                    'Perc',
                    id='yaxis-type-mcap',
                    inline=True
                )
            ], style={'width': '9%', 'float': 'right', 'display': 'inline-block'}
            )
        ]),

        html.Div([
            dcc.Graph(
                id='volume'
            )

        ], style={'height': '25%', 'width': '50%', 'float': 'left'}
        ),

        html.Div([
            dcc.Graph(
                id='market-cap'
            )

        ], style={'height': '25%', 'width': '50%', 'float': 'right'}
        ),
    ]
)


@app.callback(
    Output('market-cap', 'figure'),
    Input('yaxis-type-mcap', 'value'))
def get_market_cap_plot(yaxis_type_mcap):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=gcd['timestamp'],
                             y=(gcd['btc_market_cap_perc'] if yaxis_type_mcap == 'Perc' else gcd['btc_market_cap_perc'] * gcd['market_cap_usd']),
                             name='BTC Market Cap', line=dict(color=' #f2a900', width=4)), secondary_y=False)
    fig.add_trace(go.Scatter(x=gcd['timestamp'],
                             y=(gcd['eth_market_cap_perc'] if yaxis_type_mcap == 'Perc' else gcd['eth_market_cap_perc'] * gcd['market_cap_usd']),
                             name='ETH Market Cap', line=dict(color=' #6B8068', width=4)), secondary_y=True)
    fig.update_layout(
        paper_bgcolor='#15182B',
        plot_bgcolor='#15182B',
        title='BTC and ETH Market Caps',
        legend=dict(
            yanchor='bottom',
            y=0.99,
            xanchor='right',
            x=0.55),
        font=dict(
            family='Helvetica',
            color='#FFFFFF'
        ),
        xaxis_showgrid=False,
        yaxis_showgrid=False
    )
    fig['layout']['yaxis2']['showgrid'] = False
    fig.update_yaxes(title_text=f'''BTC Market Cap ({'%' if yaxis_type_mcap == 'Perc' else 'USD'})''', secondary_y=False)
    fig.update_yaxes(title_text=f'''ETH Market Cap ({'%' if yaxis_type_mcap == 'Perc' else 'USD'})''', secondary_y=True)
    fig.update_yaxes(type='linear' if yaxis_type_mcap == 'Perc' else 'log')
    return fig


@app.callback(
    Output('volume', 'figure'),
    Input('yaxis-type-volume', 'value'))
def get_volume_plot(yaxis_type_volume):
    price_modifier = 1 if yaxis_type_volume == 'USD' else GetFTXData().get_ticker_info('BTC', 'USD', '1h', 1).iloc[-1, 2]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=gcd['timestamp'], y=gcd['total_volume_usd']/price_modifier,
                             name='Total Crypto 24h Market Volume',
                             line=dict(color=' #4265FC', width=4)), secondary_y=False)
    fig.add_trace(go.Scatter(x=gcd['timestamp'], y=gcd['market_cap_usd']/price_modifier, name='Crypto Market Cap',
                             line=dict(color=' #3c3c3d', width=4)), secondary_y=True)
    fig.update_layout(
        paper_bgcolor='#15182B',
        plot_bgcolor='#15182B',
        title='Total Volume and Market Cap',
        legend=dict(
            yanchor='bottom',
            y=0.99,
            xanchor='right',
            x=0.66),
        font=dict(
            family='Helvetica',
            color='#FFFFFF'
        ),
        xaxis_showgrid=False,
        yaxis_showgrid=False
    )
    fig['layout']['yaxis2']['showgrid'] = False
    fig.update_yaxes(title_text=f'''Volume ({'USD' if yaxis_type_volume == 'USD' else 'BTC'})''',
                     secondary_y=False)
    fig.update_yaxes(title_text=f'''Market Cap ({'USD' if yaxis_type_volume == 'USD' else 'BTC'})''',
                     secondary_y=True)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
