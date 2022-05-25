from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
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
        title='Total Volume and Market Cap',
        legend=dict(
            yanchor="bottom",
            y=0.99,
            xanchor="right",
            x=0.66)
    )
    fig.update_yaxes(title_text="Volume (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Market Cap (USD)", secondary_y=True)
    return fig


def create_radio_table():
    table_header = [
        html.Thead(html.Tr([html.Th("Volume"), html.Th("Market Caps")]))
    ]

    row1 = html.Tr([
        html.Td(
            dcc.RadioItems(
                    ['USD', 'BTC'],
                    'USD',
                    id='yaxis-type-volume'
                )),
        html.Td(
            dcc.RadioItems(
                    ['Perc', 'USD'],
                    'Perc',
                    id='yaxis-type-mcap'
                ))
        ]
        )

    table_body = [html.Tbody([row1])]

    return dbc.Table(table_header + table_body, bordered=True)


app = Dash(__name__)

app.layout = html.Div([
        html.H1(children='Crypto Dashboard'),

        html.Div([
            dcc.Graph(
                id='volume',
                figure=get_volume_plot()
            )

        ], style={'height': '25%', 'width': '50%', 'float': 'left'}
        ),

        html.Div([
            dcc.Graph(
                id='market-cap'
            )

        ], style={'height': '25%', 'width': '50%', 'float': 'right'}
        ),

        html.Div(
            create_radio_table(),
            style={'align': 'center'}
        )

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
        plot_bgcolor='white',
        title='BTC and ETH Market Caps',
        legend=dict(
            yanchor="bottom",
            y=0.99,
            xanchor="right",
            x=0.55)
    )
    fig.update_yaxes(title_text=f'''BTC Market Cap ({'%' if yaxis_type_mcap == 'Perc' else 'USD'})''', secondary_y=False)
    fig.update_yaxes(title_text=f'''ETH Market Cap ({'%' if yaxis_type_mcap == 'Perc' else 'USD'})''', secondary_y=True)
    fig.update_yaxes(type='linear' if yaxis_type_mcap == 'Perc' else 'log')
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
