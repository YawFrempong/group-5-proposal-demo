import pandas as pd
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from urllib.request import urlopen
from statistics import mean
import json

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

app = dash.Dash(__name__)
server = app.server

radio_options = [{'label': 'View States', 'value': 'States'}, {'label': 'View Counties', 'value': 'Counties'}]
states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY',
          'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
          'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
my_color_scale = ["yellow", "orange", "red", "pink", "purple", "#19D3F3", "blue", "#00CC96", "green", "#16FF32"]

# Load Data - Zillow Home Value Index of Single Family Homes--------------------------------------------------------------------------------------------------------
df_ZHVI = pd.read_csv("single_family_home_ZHVI.csv")
main_dict_ZHVI = {}

for state in states:
    main_dict_ZHVI[state] = {}

for index, row in df_ZHVI.iterrows():
    arr = row.tolist()
    state = arr[4]
    dates = arr[5:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)

    year = 1996
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])

        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_ZHVI[state][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1

    main_dict_ZHVI[state][str(year)] = val_2021

# Load Data - Zillow Home Value Index for Single Family Homes(County)--------------------------------------------------------------------------------------------------------
df_ZHVI_county = pd.read_csv("single_family_home_ZHVI_county.csv")
df_ZHVI_county['StateCodeFIPS'] = df_ZHVI_county['StateCodeFIPS'].apply(lambda x: str(x).zfill(2))
df_ZHVI_county['MunicipalCodeFIPS'] = df_ZHVI_county['MunicipalCodeFIPS'].apply(lambda x: str(x).zfill(3))

df_ZHVI_county_FIPS = pd.DataFrame()
df_ZHVI_county_FIPS['FIPS'] = df_ZHVI_county['StateCodeFIPS'] + df_ZHVI_county['MunicipalCodeFIPS']
zhvi_county_fips = df_ZHVI_county_FIPS['FIPS'].tolist()
main_dict_ZHVI_county = {}
fip_to_county = {}

for fip in zhvi_county_fips:
    main_dict_ZHVI_county[fip] = {}

for index, row in df_ZHVI_county.iterrows():
    arr = row.tolist()
    fip = zhvi_county_fips[index]
    dates = arr[9:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)

    fip_to_county[fip] = arr[2]

    year = 1996
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])

        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_ZHVI_county[fip][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1

    main_dict_ZHVI_county[fip][str(year)] = val_2021

# Load Data - Quandl, Freddie Mac Housing Price Index--------------------------------------------------------------------------------------------------------
df_Freddie = pd.read_csv("FMAC-HPI.csv")
main_dict_Freddie = dict()

for state in states:
    group_by_date = dict()
    for index, row in df_Freddie.iterrows():
        val = row[state]
        date = row['Date'][:4]

        # add to dictionary
        if group_by_date.get(date):
            temp = group_by_date[date]
            temp.append(val)
            group_by_date[date] = temp
        else:
            group_by_date[date] = [val]

    for key in group_by_date:
        arr = group_by_date[key]
        group_by_date[key] = mean(arr)

    main_dict_Freddie[state] = group_by_date


# Functions ---------------------------------------------------------------------------------------------------------------------------------------
def update_page_layout():
    # choropleth map
    my_layout = html.Div([
        dcc.Dropdown(id='slct_dataset',
                     options=[
                         {'label': 'Freddie Mac House Price Index (1975 - 2017) *States Only*', 'value': 'FMAC'},
                         {'label': 'Zillow Home Value Index - Single Family Homes (1996 - 2021) *States & Counties*',
                          'value': 'ZHVI'},
                         {'label': 'Zillow Observed Rent Index (1996 - 2021)', 'value': 'ZORI'},
                         {
                             'label': 'Zillow For-Sale Inventory vs Newly Pending Listings vs Days to Pending - Single Family Homes (1996 - 2021)',
                             'value': 'SALES'},
                         {
                             'label': 'Data Modeling: Zillow Home Value Forecast vs Our Home Value Forecast - All Property (2022)',
                             'value': 'FORECAST'},
                         {'label': 'Data Modeling: Clustering of Home Sales and Migration', 'value': 'CLUSTER'}
                     ],
                     value='FMAC'),
        html.Br(),
        dcc.RadioItems(id="slct_view",
                       options=radio_options,
                       value='States',
                       labelStyle={'display': 'inline-block'}),
        html.Div(id='output_container', children=[]),
        html.Br(),
        dcc.Graph(id='choropleth_graph', figure={}),
        dcc.Slider(id="slct_year", min=1975, max=2021, step=1, value=2008,
                   marks={
                       1975: "1975",
                       1976: "1976",
                       1977: "1977",
                       1978: "1978",
                       1979: "1979",
                       1980: "1980",
                       1981: "1981",
                       1982: "1982",
                       1983: "1983",
                       1984: "1984",
                       1985: "1985",
                       1986: "1986",
                       1987: "1987",
                       1988: "1988",
                       1989: "1989",
                       1990: "1990",
                       1991: "1991",
                       1992: "1992",
                       1993: "1993",
                       1994: "1994",
                       1995: "1995",
                       1996: "1996",
                       1997: "1997",
                       1998: "1998",
                       1999: "1999",
                       2000: "2000",
                       2001: "2001",
                       2002: "2002",
                       2003: "2003",
                       2004: "2004",
                       2005: "2005",
                       2006: "2006",
                       2007: "2007",
                       2008: "2008",
                       2009: "2009",
                       2010: "2010",
                       2011: "2011",
                       2012: "2012",
                       2013: "2013",
                       2014: "2014",
                       2015: "2015",
                       2016: "2016",
                       2017: "2017",
                       2018: "2018",
                       2019: "2019",
                       2020: "2020",
                       2021: "2021"
                   }
                   ),
        dcc.Graph(id='line_graph', children=[]),
        html.I("Enter State/FIP Code"),
        html.Br(),
        dcc.Input(
            id="slct_state",
            type='text',
            value=''
        )
    ])

    return my_layout


# Freddie Mac HPI Webpage Content
def page_1(selected_year, state_str):
    container = ""
    dff = pd.DataFrame()
    state_code_arr = []
    hpi_arr = []
    for key in main_dict_Freddie:
        selected_state = main_dict_Freddie[key]
        selected_hpi = selected_state[str(selected_year)]
        state_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['state_code'] = state_code_arr
    dff['Housing Price Index'] = hpi_arr

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',  # require to load data to the correct states
        scope="usa",
        color='Housing Price Index',  # numerical value in dataframe to determine hue
        hover_data=['state_code', 'Housing Price Index'],
        color_continuous_scale=my_color_scale,
        labels={'Housing Price Index': 'Housing Price Index'},
        template='plotly_dark',
        range_color=[0, 400]
    )

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Housing Price Index'] = []
    title_str = 'Housing Price Index History in ' + state_str
    fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)

    if state_str.upper() in states:
        state_years = []
        state_HPIs = []
        local_dict = main_dict_Freddie[state_str.upper()]

        for key in local_dict:
            state_years.append(key)
            state_HPIs.append(local_dict[key])

        state_years.reverse()
        state_HPIs.reverse()
        df_line['Year'] = state_years
        df_line['Housing Price Index'] = state_HPIs
        fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)

    # returns to the [output, output,....] in @app.callback()
    return container, fig, fig_2


# Zillow Home Value Index Webpage Content
def page_2(selected_year, state_str):
    container = ""
    dff = pd.DataFrame()
    state_code_arr = []
    hpi_arr = []
    for key in main_dict_ZHVI:
        selected_state = main_dict_ZHVI[key]
        selected_hpi = selected_state[str(selected_year)]
        state_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['state_code'] = state_code_arr
    dff['Home Value Index'] = hpi_arr

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',  # require to load data to the correct states
        scope="usa",
        color='Home Value Index',  # numerical value in dataframe to determine hue
        hover_data=['state_code', 'Home Value Index'],
        color_continuous_scale=my_color_scale,
        labels={'Home Value Index': 'Home Value Index'},
        template='plotly_dark',
        range_color=[0, 800000]
    )

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Home Value Index History in ' + state_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if state_str.upper() in states:
        state_years = []
        state_HPIs = []
        local_dict = main_dict_ZHVI[state_str.upper()]

        for key in local_dict:
            state_years.append(key)
            state_HPIs.append(local_dict[key])

        df_line['Year'] = state_years
        df_line['Home Value Index'] = state_HPIs
        fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    # returns to the [output, output,....] in @app.callback()
    return container, fig, fig_2


def page_3(selected_year, fip_str):
    container = ""
    dff = pd.DataFrame()
    county_code_arr = []
    hpi_arr = []
    for key in main_dict_ZHVI_county:
        selected_county = main_dict_ZHVI_county[key]
        selected_hpi = selected_county[str(selected_year)]
        county_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['county_code'] = county_code_arr
    dff['Home Value Index'] = hpi_arr

    fig = px.choropleth_mapbox(dff,
                               geojson=counties,
                               locations='county_code',
                               color='Home Value Index',
                               color_continuous_scale=my_color_scale,
                               range_color=(0, 3000000),
                               # scope="usa",
                               labels={'Home Value Index': 'Home Value Index'},
                               mapbox_style="carto-positron",
                               zoom=3,
                               center={"lat": 37.0902, "lon": -95.7129},
                               )

    # get county name from fip
    if fip_to_county.get(fip_str):
        county_str = fip_to_county[fip_str]
    else:
        county_str = fip_str

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Home Value Index History in ' + county_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if fip_str in main_dict_ZHVI_county.keys():
        county_years = []
        county_HPIs = []
        local_dict = main_dict_ZHVI_county[fip_str]

        for key in local_dict:
            county_years.append(key)
            county_HPIs.append(local_dict[key])

        # county_years.reverse()
        # county_HPIs.reverse()
        df_line['Year'] = county_years
        df_line['Housing Price Index'] = county_HPIs
        fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)
    return container, fig, fig_2


# ------------------------------------------------------------------------------

app.layout = update_page_layout


# Interactive callbacks

# Given an input(year) update the output page components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='choropleth_graph', component_property='figure'),
     Output(component_id='line_graph', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_state', component_property='value'),
     Input(component_id='slct_dataset', component_property='value'),
     Input(component_id='slct_view', component_property='value')]
)
def update_graph(selected_year, state_str, selected_dataset, selected_view):
    if selected_dataset == 'FMAC':
        return page_1(selected_year, state_str)
    elif selected_dataset == 'ZHVI':
        if selected_view == 'States':
            return page_2(selected_year, state_str)
        elif selected_view == 'Counties':
            return page_3(selected_year, state_str)
    elif selected_dataset == 'ZORI':
        return page_1(selected_year, state_str)
    elif selected_dataset == 'SALES':
        return page_1(selected_year, state_str)
    elif selected_dataset == 'FORECAST':
        return page_1(selected_year, state_str)
    elif selected_dataset == 'CLUSTER':
        return page_1(selected_year, state_str)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
