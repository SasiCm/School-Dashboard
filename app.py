from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import json
from urllib.request import urlopen
import plotly.express as px

# Create DataFrame
df = pd.read_csv('school_province.csv')

# Load Thailand GeoJSON
with urlopen('https://raw.githubusercontent.com/apisit/thailand.json/master/thailandWithName.json') as response:
    thai_province = json.load(response)

dropdown = [{'label': province, 'value': province} for province in df['province'].unique()]

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div('School Dashboard', className="text-primary text-center fs-3")
    ]),

    dbc.Row([
        dcc.Dropdown(
            id='dropdown-province',
            options=dropdown,
            value=df['province'].iloc[0],  # Default to the first province
            clearable=False,
            style={'width': '50%'}
        )
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='choropleth-map')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='pie-chart')
        ], width=6),
    ]),
], fluid=True)

# Callback to update pie chart based on selected province
@app.callback(
    Output('pie-chart', 'figure'),
    Input('dropdown-province', 'value')
)
def update_pie_chart(selected_province):
    filtered_df = df[df['province'] == selected_province]
    
    # Calculate total male and female students
    total_male = filtered_df['totalmale'].sum()
    total_female = filtered_df['totalfemale'].sum()
    
    # Create labels and values for pie chart
    labels = ['ผู้ชาย', 'ผู้หญิง']
    values = [total_male, total_female]
    
    # Create pie chart figure
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    
    # Update layout
    fig.update_layout(title=f'นักเรียนที่จบชั้นมัธยมศึกษาปีที่ 6 ปีการศึกษา 2566 จังหวัด {selected_province}',
                      showlegend=True)
    
    return fig

# Callback to update choropleth map based on selected province
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('dropdown-province', 'value')
)
def update_choropleth_map(selected_province):
    filtered_df = df[df['province'] == selected_province]

    fig = px.choropleth_mapbox(
        filtered_df,
        geojson=thai_province,
        featureidkey="properties.name",
        locations="province",
        color="totalstd",
        color_continuous_scale="sunsetdark",
        hover_name="schools_province",
        mapbox_style="open-street-map",
        center={"lat": 14.11, "lon": 100.35},
        zoom=5,
        labels={
            "province": "จังหวัด",
            "totalstd": "นักเรียนทั้งหมด",
        },
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
