import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from dash_table import DataTable

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

########### Set up the layout
app.layout = html.Div([
    html.Label('Max Interest Rate (%): '),
    dcc.Input(id='rate', type='number'),
    
    html.Br(),
    
    html.Label('Max Year: '),
    dcc.Input(id='year', type='number'),
    
    dcc.Graph(id='graph'),
    
    DataTable(
        id='table',
    ),
])

@app.callback(
    [
        Output(component_id='graph', component_property='figure'),
        Output(component_id='table', component_property='columns'),
        Output(component_id='table', component_property='data'),
    ],
    [
        Input(component_id='rate', component_property='value'),
        Input(component_id='year', component_property='value'),
    ]
)
def update(maxRate, maxYear):
    rates=[i for i in range(1, maxRate+1)]
    years=[n for n in range(1, maxYear+1)]
    data=[]
    
    for i in rates:
        data.append(
            dict(
                x=years,
                y=[round((1-(1+i/100)**-n)/i*100, 4) for n in years],
                name=f'{i}%'
            )
        )
    
    matrix=[trace['y'] for trace in data]
    tposed=[[row[j] for row in matrix] for j in range(len(matrix[0]))]
    
    columns=[dict(name=x['name'], id=x['name']) for x in data]
    sheet=[{column['id']: value for column, value in zip(columns, row)} for i, row in enumerate(tposed)]
    
    columns.insert(0, dict(name='Year', id='Year'))
    for i, row in enumerate(sheet):
        row['Year']=i+1
    
    return (
        dict(
            data=data,
            layout=dict(
                xaxis=dict(
                    title='Year'
                ),
                yaxis=dict(
                    title='Present Value'
                ),
            )
        ),
        columns,
        sheet
    )

if __name__ == '__main__':
    app.run_server()
