import os
import requests
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html, callback
import geopandas as gpd

DATASET1_URL = "https://drive.google.com/uc?export=download&id=1ePenLkW0ObjodzXtvLFpJu-PthLOD82P"
DATASET2_URL = "https://drive.google.com/uc?export=download&id=1q1YXEZgMLyZceQdhc8buToaMtGg0G1IE"
DATASET1_PATH = os.path.abspath('datasets/WHR2023.csv')
DATASET2_PATH = os.path.abspath('datasets/WHR.csv')
world_geo = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))


def download(url, filename="Dataset.csv"):
    if os.path.exists(filename):
        print("File already exists")
        return filename

    try:
        if not os.path.exists("datasets"):
            os.mkdir("datasets")
        res = requests.get(url)
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"Download successful: {filename}")
    except requests.RequestException as e:
        raise ValueError(f"Error downloading file: {e}") from e

    return filename


df = pd.read_csv(download(DATASET2_URL, DATASET2_PATH))
print(df.head())

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children="World Happiness Report", style={"text-align": "center"}),
    html.Hr(),
    html.Div(children=[
        html.H2(children="Happiness of a country", style={'text-align': 'center'}),
        dcc.Dropdown(df["Country Name"].unique(), "India", id="country-selection"),
        dcc.Graph(id="country-happiness")
    ]),
    html.Hr(),
    html.Div(children=[
        html.H2(children="Compare Countries against World Happiness", style={"text-align": "center"}),
        dcc.Dropdown(df["Country Name"].unique(), id="country-comparison-selection", multi=True,
                     value=["India", "China", "Pakistan"]),
        dcc.Graph(id="country-comparison")
    ]),
    html.Hr(),
    html.Div(children=[
        html.H2(children="World Happiness over the years", style={"text-align": "center"}),
        dcc.Dropdown(df["Year"].unique(), id="world-year-selection"),
        dcc.Graph(id="world-happiness")
    ])

])


@callback(
    Output("country-happiness", 'figure'),
    Input("country-selection", "value")
)
def update_graph(value):
    dff = df[df["Country Name"] == value]
    figure = px.line(dff, x="Year", y="Life Ladder", text="Year")
    figure.update_traces(textposition="bottom right")
    return figure


@callback(
    Output("country-comparison", "figure"),
    Input("country-comparison-selection", "value")
)
def country_comparison(countries):
    dff = df[df["Country Name"].isin(countries)]
    # dff = dff[["Year", "Life Ladder", "Country Name"]]
    return px.bar(dff, x="Year", y="Life Ladder", color="Country Name", barmode="group")


@callback(
    Output("world-happiness", "figure"),
    Input("world-year-selection", "value")
)
def world_comparison(year):
    figure = px.choropleth(df, locations='Country Code', color='Life Ladder', hover_name='Country Name',
                           projection='natural earth', animation_frame='Year',
                           title='Happiness Over the Ears')
    return figure


if __name__ == "__main__":
    app.run(debug=True)
