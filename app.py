import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from dash_table import DataTable

from random import uniform

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

def getPairs(string):
    row=list(map(float, string.split()))
    return [row[i: i+2] for i in range(len(row)) if i%2==0]

def transpose(matrix):
    return [[row[j] for row in matrix] for j in range(len(matrix[0]))]

def getA(xlist, degrees):
    return [[x**degree for degree in range(degrees+1)] for x in xlist]

def dot(u, v):
    return sum([x*y for x, y in zip(u, v)])

def multiply(a, b):
    return [[dot(row, column) for column in transpose(b)] for row in a]

def augment(a, b):
    return [x+y for x, y in zip(a, b)]

def getConstant(v):
    for x in v:
        if x!=0:
            return x

def simplify(v):
    constant=getConstant(v)
    return [x/constant for x in v]

def clear(u, v):
    i=u.index(1)
    constant=v[i]
    return [y-constant*x for x, y in zip(u, v)]

def randX(down, up):
    return sorted([uniform(down, up) for i in range(99)])

def getY(x, degrees):
    a=getA(x, degrees)
    return [dot(a0, coefs) for a0 in a]

def reduce(matrix):
    height=len(matrix)
    
    for i in range(height):
        matrix[i]=simplify(matrix[i])
        
        for j in range(i+1, height):
            matrix[j]=clear(matrix[i], matrix[j])
            
    for i in range(height):
        for j in range(i+1, height):
            matrix[i]=clear(matrix[j], matrix[i])
            
    return matrix

def getCoefs(x, y, degrees):
    a=getA(x, degrees)
    aT=transpose(a)
    
    b=[[y0] for y0 in y]
    
    aTa=multiply(aT, a)
    aTb=multiply(aT, b)
    
    system=augment(aTa, aTb)
    
    return [row[-1] for row in reduce(system)]

app.layout = html.Div([
    html.H1('Least-Squares Regression'),
    
    html.Label('Space-Separated Data: '),
    dcc.Input(id='points'),
    html.Br(),

    html.Label('For example, input points (1, 0), (2, 3), (3, 7), (4, 14), (5, 22) as 1 0 2 3 3 7 4 14 5 22'),
    html.Br(),
    html.Br(),

    html.Label('Degrees of Best-Fit Line: '),
    dcc.Input(id='degrees', type='number', value=-1),
    
    html.Div(id='eq'),
    html.Br(),

    html.Label('Model Prediction for x = '),
    dcc.Input(id='x', type='number'),
    html.Br(),
    html.Div(id='y'),
    
    dcc.Graph(id='graph'),    
])

coefs=1

@app.callback(
    [
        Output('graph', 'figure'),
        Output('eq', 'children'),
    ],
    [
        Input('points', 'value'),
        Input('degrees', 'value'),
    ]
)
def fillChart(points, degrees):
    x, y=transpose(getPairs(points))
    eq=''
          
    traces=[
        dict(
            x=x,
            y=y,
            mode='markers',
            name='Data'
        )
    ]
    
    if degrees>=0:
        global coefs
        coefs=getCoefs(x, y, degrees)

        x1=randX(min(x), max(x))
        y1=getY(x1, degrees)

        traces.append(
            dict(
                x=x1,
                y=y1,
                name='Line of Best Fit'
            )
        )
        
        eq=f'Model: f (x, {degrees}) = ' + ' + '.join([f'({round(coef, 9)}) x^{i}' for i, coef in enumerate(coefs)])
    
    return (
        dict(
            data=traces,
            layout=dict(
                hovermode='closest'
            )
        ),
        eq,
    )

@app.callback(
    Output('y', 'children'),
    [
        Input('x', 'value'),
        Input('degrees', 'value'),
    ]
)
def predict(x, degrees):       
    return f'f ({x}, {degrees}) = {round(getY([x], degrees)[0], 9)}'

if __name__ == '__main__':
    app.run_server()
