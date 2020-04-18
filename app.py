import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def load_graph(is_logged=False):
    csv = 'https://raw.githubusercontent.com/archiewood/lightlogger/master/lightlog.csv'
    avg_window=5

    df = pd.read_csv(csv)
    df['date']=df['timestamp'].str[:10]
    df['time']=df['timestamp'].str[10:19]
    df['median']= df['light_reading'].rolling(avg_window).median()
    df['std'] = df['light_reading'].rolling(avg_window).std()
    df = df[(df.light_reading <= df['median']+3*df['std']) & (df.light_reading >= df['median']-3*df['std'])]
    df['light_reading_moving_avg'] = df.iloc[:,1].rolling(window=avg_window).mean()
    
    df['hour']=df['timestamp'].str[11:13].astype(float)
    df['minute']=df['timestamp'].str[14:16].astype(float)
    df['minute_interval']=df['minute'].floordiv(6)
    df['hour-decimal']=df['hour']+df['minute_interval']/10
    df['date']=df['timestamp'].str[:10]
    
    piv=df.pivot_table(index=['hour-decimal','date'],values='light_reading_moving_avg').reset_index()
    
    if is_logged:
        fig= px.line(piv,x='hour-decimal',y='light_reading_moving_avg',color='date',range_x=[9,21],range_y=[0.1,1000],title='Balcony Light Intensity',log_y=True)
    else:
        fig= px.line(piv,x='hour-decimal',y='light_reading_moving_avg',color='date',range_x=[9,21],range_y=[0,100],title='Balcony Light Intensity')
        
        
    return fig 


app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Light on my Balcony',style={'textAlign': 'left'}
           ),
    html.Div(children='''
        A little web app that shows when there is light on my balcony, as measured by an LDR using a Raspberry Pi.
    
    ''',style={'textAlign': 'left'}),
    
    html.Div(
        children=[
            html.Label('Light Intensity Axis',style={'textAlign':'right'}),
            dcc.RadioItems(
                id='log_switch',
                options=[
                    {'label': 'Linear', 'value': False},
                    {'label': 'Log', 'value': True}
                ],
                value=True,style={'textAlign':'right'}
            ),
            dcc.Graph(id='logged_chart',figure=load_graph(is_logged=True))],
        style = { 'height': '40px','margin': '0 auto'}
    ),
    

])

@app.callback(
    Output(component_id='logged_chart', component_property='figure'),
    [Input(component_id='log_switch', component_property='value')]
)
def update_output_chart(log_choice):
    return load_graph(is_logged=log_choice)



if __name__ == '__main__':
    app.run_server(debug=False)