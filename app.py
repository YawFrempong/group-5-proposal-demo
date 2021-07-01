import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from urllib.request import urlopen
from statistics import mean
import numpy as np
import json
import math

from pycaret.clustering import *

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

app = dash.Dash(__name__)
server = app.server

radio_options = [{'label': 'View States', 'value': 'States'}, {'label': 'View Counties', 'value': 'Counties'}, {'label': 'View Cities', 'value': 'Cities'}]
radio_options_2 = [{'label': 'For Sale Homes', 'value': 'for_sale'}, {'label': 'Pending Home Sales', 'value': 'pending'}, {'label': 'For Sale to Pending - Sale Speed', 'value': 'sale_speed'}, {'label': 'Homes Sold', 'value': 'sold'}]
states = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']
my_color_scale = ["yellow", "orange", "red", "pink", "purple", "#19D3F3", "blue", "#00CC96", "green", "#16FF32"]
first_load = True
new_dff_ZHVI_cities = pd.DataFrame()
prev_year = -1

#Load Data - Zillow Home Value Index for Single Family Homes--------------------------------------------------------------------------------------------------------
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

#Load Data - Zillow Home Value Index for Single Family Homes(County)--------------------------------------------------------------------------------------------------------
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
#Load Data - Zillow Home Value Index for Single Family Homes(City)--------------------------------------------------------------------------------------------------------

df_city = pd.read_csv('./us_cities_lat_long.csv', usecols=['CITY','LATITUDE','LONGITUDE'])
city_to_coor = {}

for index, row in df_city.iterrows():
    arr = row.tolist()
    city = arr[0]
    coordinate = [arr[1],arr[2]]
    city_to_coor[city] = coordinate

df_ZHVI_city = pd.read_csv("single_family_home_ZHVI_city.csv")
df_ZHVI_city = df_ZHVI_city[:1400]
cities_ZHVI = df_ZHVI_city['RegionName'].to_list()
main_dict_ZHVI_city = {}

for city in cities_ZHVI:
    main_dict_ZHVI_city[city] = {}

for index, row in df_ZHVI_city.iterrows():
    arr = row.tolist()
    city = arr[2]
    dates = arr[8:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)
    
    year = 1996
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])
        
        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_ZHVI_city[city][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1
            
    main_dict_ZHVI_city[city][str(year)] = val_2021

#Load Data - Zillow Rental Property--------------------------------------------------------------------------------------------------------
df_rentals = pd.read_csv("Rental_Averages.csv")

year_val_rentals = []
for key, column in df_rentals.iteritems():
    try:
        int_v = int(key)
    except ValueError:
        continue
    year_val_rentals.append(int_v)

main_dict_rentals = {}
for index, row in df_rentals.iterrows():
    values = row.values
    state_name = values[1]
    cur_vals = values[2:]
    if state_name not in main_dict_rentals.keys():
        main_dict_rentals[state_name] = {}
        for i, year in enumerate(year_val_rentals, 0):
            if year not in main_dict_rentals[state_name].keys():
                main_dict_rentals[state_name][year] = {}
            main_dict_rentals[state_name][year] = cur_vals[i]

#Load Data - Zillow For Sale--------------------------------------------------------------------------------------------------------
df_for_sale = pd.read_csv("for_sale.csv")
main_dict_for_sale = {}
cities_ZHVI = df_for_sale['RegionName'].to_list()

for city in cities_ZHVI:
    city_clean = city.split(',')[0]
    main_dict_for_sale[city_clean] = {}

for index, row in df_for_sale.iterrows():
    arr = row.tolist()
    city = arr[2].split(',')[0]
    dates = arr[8:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)
    
    year = 2018
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])
        
        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_for_sale[city][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1
            
    main_dict_for_sale[city][str(year)] = val_2021
#Load Data - Zillow Pending--------------------------------------------------------------------------------------------------------
df_pending = pd.read_csv("pending.csv")

main_dict_pending = {}
cities_ZHVI = df_pending['RegionName'].to_list()

for city in cities_ZHVI:
    city_clean = city.split(',')[0]
    main_dict_pending[city_clean] = {}

for index, row in df_pending.iterrows():
    arr = row.tolist()
    city = arr[2].split(',')[0]
    dates = arr[8:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)
    
    year = 2018
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])
        
        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_pending[city][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1
            
    main_dict_pending[city][str(year)] = val_2021

#Load Data - Zillow Sale to Pending--------------------------------------------------------------------------------------------------------
df_speed = pd.read_csv("sale_speed.csv")
main_dict_speed = {}
cities_ZHVI = df_speed['RegionName'].to_list()

for city in cities_ZHVI:
    city_clean = city.split(',')[0]
    main_dict_speed[city_clean] = {}

for index, row in df_speed.iterrows():
    arr = row.tolist()
    city = arr[2].split(',')[0]
    dates = arr[8:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)
    
    year = 2018
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])
        
        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_speed[city][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1
            
    main_dict_speed[city][str(year)] = val_2021
#Load Data - Zillow Homes Sold--------------------------------------------------------------------------------------------------------
df_sold = pd.read_csv("sale_count.csv")
main_dict_sold = {}
cities_ZHVI = df_sold['RegionName'].to_list()

for city in cities_ZHVI:
    city_clean = city.split(',')[0]
    main_dict_sold[city_clean] = {}

for index, row in df_sold.iterrows():
    arr = row.tolist()
    city = arr[2].split(',')[0]
    dates = arr[8:-3]
    arr_2021 = arr[-3:]
    val_2021 = mean(arr_2021)
    
    year = 2008
    dates_temp = []
    for i in range(len(dates)):
        dates_temp.append(dates[i])
        
        if len(dates_temp) == 12 or i == (len(dates) - 1):
            main_dict_sold[city][str(year)] = mean(dates_temp)
            dates_temp = []
            year += 1
            
    main_dict_sold[city][str(year)] = val_2021
#Load Data - Quandl, Freddie Mac Housing Price Index--------------------------------------------------------------------------------------------------------
df_Freddie = pd.read_csv("FMAC-HPI.csv")
main_dict_Freddie = dict()

for state in states:
    group_by_date = dict()
    for index, row in df_Freddie.iterrows():
        val = row[state]
        date = row['Date'][:4]

        #add to dictionary
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

#Load Data - Forecast--------------------------------------------------------------------------------------------------------
forecast = pd.read_csv('forecast.csv')
pop = pd.read_csv('population-msa.csv')
pop = pop[pop['year'] == 2008]
cities = pd.read_csv('us_cities_lat_long.csv',usecols=['CITY', 'LATITUDE', 'LONGITUDE','COUNTY'])

#Load Data - Cluster-----------------------------------------------------------------------
zhvi = pd.read_csv('single_family_home_ZHVI_city.csv')
sale = pd.read_csv('homesale_inventory.csv')
sold = pd.read_csv('pending_inventory.csv')
#Functions ---------------------------------------------------------------------------------------------------------------------------------------
def update_page_layout():
    # choropleth map
    my_layout = html.Div([
        dcc.Dropdown(id='slct_dataset',
            options=[
                {'label': 'Freddie Mac House Price Index (1975 - 2017) *States Only*', 'value': 'FMAC'},
                {'label': 'Zillow Home Value Index - Single Family Homes (1996 - 2021) *States, Counties, & Cities*', 'value': 'ZHVI'},
                {'label': 'Zillow Observed Rent Index (1996 - 2021) *States Only*', 'value': 'ZORI'},
                {'label': 'Zillow For-Sale Inventory vs Newly Pending Listings vs Days to Pending vs Homes Sold - Single Family Homes (1996 - 2021) *Cities Only*', 'value': 'SALES'},
                {'label': 'Data Modeling: Zillow Home Value Forecast vs Our Home Value Forecast - All Property (2022)', 'value': 'FORECAST'},
                {'label': 'Data Modeling: Clustering of Home Sales and Migration', 'value': 'CLUSTER'}
            ],
        value='FMAC'),
        html.Br(),
        dcc.RadioItems(id="slct_view",
            options=radio_options,
            value='States',
            labelStyle={'display': 'inline-block'}),
        dcc.RadioItems(id="slct_sale",
            options=radio_options_2,
            value='for_sale',
            labelStyle={'display': 'inline-block'}),
        html.Div(id='output_container', children=[]),  
        html.Br(),
        dcc.Graph(id='choropleth_graph', figure={}),
        dcc.Slider(id="slct_year", min=1975, max=2021, step=1, value=2009,
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
        html.I("Enter State Code/County FIP Code/Cities Name"),
        html.Br(),
        dcc.Input(
            id="slct_state",
            type='text',
            value=''
        )
    ])

    return my_layout



#Freddie Mac HPI Webpage Content
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
        locations='state_code', #require to load data to the correct states
        scope="usa",
        color='Housing Price Index',   #numerical value in dataframe to determine hue
        hover_data=['state_code', 'Housing Price Index'],
        color_continuous_scale=my_color_scale,
        labels={'Housing Price Index': 'Housing Price Index'},
        template='plotly_dark',
        range_color=[0,400]
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

    #returns to the [output, output,....] in @app.callback()
    return container, fig, fig_2

#Zillow Home Value Index Webpage Content
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
        locations='state_code', #require to load data to the correct states
        scope="usa",
        color='Home Value Index',   #numerical value in dataframe to determine hue
        hover_data=['state_code', 'Home Value Index'],
        color_continuous_scale=my_color_scale,
        labels={'Home Value Index': 'Home Value Index'},
        template='plotly_dark',
        range_color=[0,800000]
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

    #returns to the [output, output,....] in @app.callback()
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
        #scope="usa",
        labels={'Home Value Index':'Home Value Index'},
        mapbox_style="carto-positron",
        zoom=3, 
        center = {"lat": 37.0902, "lon": -95.7129},
                          )


    #get county name from fip
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
        
        #county_years.reverse()
        #county_HPIs.reverse()
        df_line['Year'] = county_years
        df_line['Housing Price Index'] = county_HPIs
        fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)
    return container, fig, fig_2

def page_4(selected_year, city_str):
    global first_load
    global new_dff_ZHVI_cities
    global prev_year

    container = ""
    dff = pd.DataFrame()
    city_code_arr = []
    hpi_arr = []

    for key in main_dict_ZHVI_city:
        selected_city = main_dict_ZHVI_city[key]
        selected_hpi = selected_city[str(selected_year)]
        city_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['city'] = city_code_arr
    dff['Home Value Index'] = hpi_arr

    if first_load or selected_year != prev_year:
        new_dff_ZHVI_cities = pd.DataFrame()
        prev_year = selected_year
        first_load = False
        for index, row in dff.iterrows():
            temp_city = row['city']
            
            if city_to_coor.get(temp_city) and not np.isnan(row['Home Value Index']):
                temp_lat = city_to_coor[temp_city][0]
                temp_long = city_to_coor[temp_city][1]
                temp_city_info = row['city'] + ' - Home Value Index: ' + str(row['Home Value Index'])
                new_dff_ZHVI_cities = new_dff_ZHVI_cities.append({'city':temp_city_info , 'Home Value Index':row['Home Value Index'], 'lat':temp_lat, 'long':temp_long}, ignore_index = True)

    new_dff_ZHVI_cities = new_dff_ZHVI_cities.sort_values('Home Value Index', ascending=False)

    limits = [(0,280),(281,560),(561,840),(841,1120),(1121,1400)]
    colors = ["purple","royalblue","lightseagreen","orange","yellow"]
    scale = 25000

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        new_dff_sub = new_dff_ZHVI_cities[lim[0]:lim[1]]
        
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lat = new_dff_sub['lat'],
            lon = new_dff_sub['long'],
            text = new_dff_sub['city'],
            marker = dict(size = new_dff_sub['Home Value Index']/scale, color = colors[i], line_color='rgb(40,40,40)', line_width=0.5, sizemode = 'area'),
            name = '{0} - {1}'.format(lim[0],lim[1])))

    fig.update_layout(title_text = 'Demo', showlegend = True, geo = dict(scope = 'usa', landcolor = 'rgb(217, 217, 217)',))

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Home Value Index History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if city_str in main_dict_ZHVI_city.keys():
            county_years = []
            county_HPIs = []
            local_dict = main_dict_ZHVI_city[city_str]

            for key in local_dict:
                county_years.append(key)
                county_HPIs.append(local_dict[key])
            
            df_line['Year'] = county_years
            df_line['Housing Price Index'] = county_HPIs
            fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)

    return container, fig, fig_2

def page_5(selected_year, city_str):
    container = ""

    hover_arr = []
    state_arr = []

    for state_name_key, avg_values in main_dict_rentals.items():
        selected_avg = avg_values[selected_year]

        state_arr.append(state_name_key)
        hover_arr.append(selected_avg)

    df_rentals['state_code'] = state_arr
    df_rentals['Rental Avg'] = hover_arr

    fig = px.choropleth(
        data_frame=df_rentals,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='Rental Avg',
        hover_data=['state_code', 'Rental Avg'],
        color_continuous_scale=px.colors.sequential.YlGnBu,
        labels={'Rental Avg': 'Rental Avg'},
        template='plotly_dark'
    )

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Rental Prices History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if city_str in main_dict_rentals.keys():
            county_years = []
            county_HPIs = []
            local_dict = main_dict_rentals[city_str]

            for key in local_dict:
                county_years.append(key)
                county_HPIs.append(local_dict[key])
            
            df_line['Year'] = county_years
            df_line['Housing Price Index'] = county_HPIs
            fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)

    return container, fig, fig_2

def page_6(selected_year, city_str):
    container = ""
    dff = pd.DataFrame()
    city_code_arr = []
    hpi_arr = []
    for key in main_dict_for_sale:
        selected_city = main_dict_for_sale[key]
        selected_hpi = selected_city[str(selected_year)]
        city_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['city'] = city_code_arr
    dff['Home Value Index'] = hpi_arr
    new_dff = pd.DataFrame()

    for index, row in dff.iterrows():
        temp_city = row['city']
        
        if city_to_coor.get(temp_city) and not math.isnan(row['Home Value Index']):
            temp_lat = city_to_coor[temp_city][0]
            temp_long = city_to_coor[temp_city][1]
            temp_city_info = row['city'] + ' - Homes For Sale: ' + str(round(row['Home Value Index']))
            new_dff = new_dff.append({'city':temp_city_info , 'Home Value Index':round(row['Home Value Index']), 'lat':temp_lat, 'long':temp_long}, ignore_index = True)

    new_dff = new_dff.sort_values('Home Value Index', ascending=False)

    limits = [(0,18), (19,36), (37,54), (55, 72), (73,90)]
    colors = ["purple","royalblue","lightseagreen","orange","yellow"]
    scale = 250

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        new_dff_sub = new_dff[lim[0]:lim[1]]
        
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lat = new_dff_sub['lat'],
            lon = new_dff_sub['long'],
            text = new_dff_sub['city'],
            marker = dict(size = new_dff_sub['Home Value Index']/scale, color = colors[i], line_color='rgb(40,40,40)', line_width=0.5, sizemode = 'area'),
            name = '{0} - {1}th'.format(lim[0],lim[1])))
        
    fig.update_layout(
        title_text = 'Demo',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )
    
    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Home Value Index History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if city_str in main_dict_for_sale.keys():
            county_years = []
            county_HPIs = []
            local_dict = main_dict_for_sale[city_str]

            for key in local_dict:
                county_years.append(key)
                county_HPIs.append(local_dict[key])
            
            df_line['Year'] = county_years
            df_line['Housing Price Index'] = county_HPIs
            fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)
    
    return container, fig, fig_2

def page_7(selected_year, city_str):
    container = ""
    dff = pd.DataFrame()
    city_code_arr = []
    hpi_arr = []
    for key in main_dict_pending:
        selected_city = main_dict_pending[key]
        selected_hpi = selected_city[str(selected_year)]
        city_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['city'] = city_code_arr
    dff['Home Value Index'] = hpi_arr
    new_dff = pd.DataFrame()

    for index, row in dff.iterrows():
        temp_city = row['city']
        
        if city_to_coor.get(temp_city) and not math.isnan(row['Home Value Index']):
            temp_lat = city_to_coor[temp_city][0]
            temp_long = city_to_coor[temp_city][1]
            temp_city_info = row['city'] + ' - Pending Home Sales: ' + str(round(row['Home Value Index']))
            new_dff = new_dff.append({'city':temp_city_info , 'Home Value Index':round(row['Home Value Index']), 'lat':temp_lat, 'long':temp_long}, ignore_index = True)

    new_dff = new_dff.sort_values('Home Value Index', ascending=False)

    limits = [(0,7), (8,14), (15,21), (22, 28), (29,40)]
    colors = ["purple","royalblue","lightseagreen","orange","yellow"]
    scale = 25

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        new_dff_sub = new_dff[lim[0]:lim[1]]
        
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lat = new_dff_sub['lat'],
            lon = new_dff_sub['long'],
            text = new_dff_sub['city'],
            marker = dict(size = new_dff_sub['Home Value Index']/scale, color = colors[i], line_color='rgb(40,40,40)', line_width=0.5, sizemode = 'area'),
            name = '{0} - {1}th'.format(lim[0],lim[1])))

    fig.update_layout(
        title_text = 'Demo',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Pending Home Sale History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if city_str in main_dict_pending.keys():
            county_years = []
            county_HPIs = []
            local_dict = main_dict_pending[city_str]

            for key in local_dict:
                county_years.append(key)
                county_HPIs.append(local_dict[key])
            
            df_line['Year'] = county_years
            df_line['Housing Price Index'] = county_HPIs
            fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)
    
    return container, fig, fig_2

def page_8(selected_year, city_str):
    container = ""
    dff = pd.DataFrame()
    city_code_arr = []
    hpi_arr = []
    for key in main_dict_speed:
        selected_city = main_dict_speed[key]
        selected_hpi = selected_city[str(selected_year)]
        city_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['city'] = city_code_arr
    dff['Home Value Index'] = hpi_arr
    new_dff = pd.DataFrame()

    for index, row in dff.iterrows():
        temp_city = row['city']
        
        if city_to_coor.get(temp_city) and not math.isnan(row['Home Value Index']):
            temp_lat = city_to_coor[temp_city][0]
            temp_long = city_to_coor[temp_city][1]
            temp_city_info = row['city'] + ' - Days to Pending: ' + str(round(row['Home Value Index']))
            new_dff = new_dff.append({'city':temp_city_info , 'Home Value Index':round(row['Home Value Index']), 'lat':temp_lat, 'long':temp_long}, ignore_index = True)

    new_dff = new_dff.sort_values('Home Value Index', ascending=True)

    limits = [(0,17), (18,34), (35,51), (52, 68), (69,85)]
    colors = ["purple","royalblue","lightseagreen","orange","yellow"]
    scale = 0.5

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        new_dff_sub = new_dff[lim[0]:lim[1]]
        
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lat = new_dff_sub['lat'],
            lon = new_dff_sub['long'],
            text = new_dff_sub['city'],
            marker = dict(size = new_dff_sub['Home Value Index']/scale, color = colors[i], line_color='rgb(40,40,40)', line_width=0.5, sizemode = 'area'),
            name = '{0} - {1} th'.format(lim[0],lim[1])))

    fig.update_layout(
        title_text = 'Demo',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Pending Home Sale History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if city_str in main_dict_speed.keys():
        county_years = []
        county_HPIs = []
        local_dict = main_dict_speed[city_str]

        for key in local_dict:
            county_years.append(key)
            county_HPIs.append(local_dict[key])
        
        df_line['Year'] = county_years
        df_line['Housing Price Index'] = county_HPIs
        fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)

    return container, fig, fig_2


def page_9(selected_year, city_str):
    container = ""
    dff = pd.DataFrame()
    city_code_arr = []
    hpi_arr = []
    for key in main_dict_sold:
        selected_city = main_dict_sold[key]
        selected_hpi = selected_city[str(selected_year)]
        city_code_arr.append(key)
        hpi_arr.append(selected_hpi)

    dff['city'] = city_code_arr
    dff['Home Value Index'] = hpi_arr
    new_dff = pd.DataFrame()

    for index, row in dff.iterrows():
        temp_city = row['city']
        
        if city_to_coor.get(temp_city) and not math.isnan(row['Home Value Index']):
            temp_lat = city_to_coor[temp_city][0]
            temp_long = city_to_coor[temp_city][1]
            temp_city_info = row['city'] + ' - Homes Sold: ' + str(round(row['Home Value Index']))
            new_dff = new_dff.append({'city':temp_city_info , 'Home Value Index':round(row['Home Value Index']), 'lat':temp_lat, 'long':temp_long}, ignore_index = True)

    new_dff = new_dff.sort_values('Home Value Index', ascending=False)

    limits = [(0,17), (18,34), (35,51), (52, 68), (69,85)]
    colors = ["purple","royalblue","lightseagreen","orange","yellow"]
    scale = 10

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        new_dff_sub = new_dff[lim[0]:lim[1]]
        
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lat = new_dff_sub['lat'],
            lon = new_dff_sub['long'],
            text = new_dff_sub['city'],
            marker = dict(size = new_dff_sub['Home Value Index']/scale, color = colors[i], line_color='rgb(40,40,40)', line_width=0.5, sizemode = 'area'),
            name = '{0} - {1} th'.format(lim[0],lim[1])))

    fig.update_layout(
        title_text = 'Demo',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Pending Home Sale History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    if city_str in main_dict_sold.keys():
            county_years = []
            county_HPIs = []
            local_dict = main_dict_sold[city_str]

            for key in local_dict:
                county_years.append(key)
                county_HPIs.append(local_dict[key])
            
            df_line['Year'] = county_years
            df_line['Housing Price Index'] = county_HPIs
            fig_2 = px.line(df_line, x="Year", y="Housing Price Index", title=title_str)

    return container, fig, fig_2

def page_10(selected_year, city_str):
    container =""
    merged_forecasts = pd.merge(forecast,cities,how = 'inner', left_on = 'CityName',right_on = 'CITY')
    merged_forecasts['CountyName'] = merged_forecasts.apply(lambda row: row['CountyName'].replace(' County',''), axis = 1)
    merged_forecasts = merged_forecasts[merged_forecasts['CountyName'] == merged_forecasts['COUNTY']]
    merged_forecasts[(merged_forecasts['CityName'] == 'Springfield') & (merged_forecasts['CountyName'] == 'Hampden')]
    merged_forecasts[(merged_forecasts['CityName'] == 'Springfield') & (merged_forecasts['CountyName'] == 'Hampden')]['ForecastYoYPctChange'].mean()
    merged_forecasts = merged_forecasts.groupby(['CityName','CountyName','StateName']).mean()
    merged_forecasts.sort_values('ForecastYoYPctChange',ascending = False, inplace=True)
    merged_forecasts.reset_index(inplace=True)
    merged_forecasts['text'] = merged_forecasts.apply(lambda row: '{0},{1} -- Projected change in price: {2}%'.format(row['CityName'], row['StateName'], row['ForecastYoYPctChange']),axis = 1)
    limits = [(0,200),(18809,18879)]
    colors = ["lightseagreen", "crimson",]
    names = ['Positive Zillow Home Value Index Forecast', 'Negative Zillow Home Value Index Forecast']
    scale = 7

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        df_sub = merged_forecasts[lim[0]:lim[1]]
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lon = df_sub['LONGITUDE'],
            lat = df_sub['LATITUDE'],
            text = df_sub['text'],
            marker = dict(
                size = abs(df_sub['ForecastYoYPctChange'])*scale,
                color = colors[i],
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode = 'area'
            ),
            name = names[i]))

    fig.update_layout(
        title_text = '2022 US Zillow Home Value Index forecasts',
        showlegend = True,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )
    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Pending Home Sale History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    return container, fig, fig_2

def page_11(selected_year, city_str):
    container =""
    fig = go.Figure()

    sale.drop(['2017-11-30', '2017-12-31'],axis = 1, inplace=True)
    sold.drop(['RegionID', 'SizeRank','RegionType', 'StateName'],axis = 1, inplace=True)
    supply_demand = pd.merge(sale,sold,how = 'inner', on = 'RegionName', suffixes = ['_for_sale','_sold'])

    dates = ['2018-01-31', '2018-02-28', '2018-03-31', '2018-04-30', '2018-05-31',
        '2018-06-30', '2018-07-31', '2018-08-31', '2018-09-30', '2018-10-31',
        '2018-11-30', '2018-12-31', '2019-01-31', '2019-02-28', '2019-03-31',
        '2019-04-30', '2019-05-31', '2019-06-30', '2019-07-31', '2019-08-31',
        '2019-09-30', '2019-10-31', '2019-11-30', '2019-12-31', '2020-01-31',
        '2020-02-29', '2020-03-31', '2020-04-30', '2020-05-31', '2020-06-30',
        '2020-07-31', '2020-08-31', '2020-09-30', '2020-10-31', '2020-11-30',
        '2020-12-31', '2021-01-31', '2021-02-28', '2021-03-31']

    supply_demand['CityName'] = supply_demand.apply(lambda row: row['RegionName'].split(',')[0], axis = 1)
    supply_demand['CityName'].replace('Miami-Fort Lauderdale', 'Miami',inplace=True)
    supply_demand['CityName'].replace('Minneapolis-St Paul', 'Minneapolis',inplace=True)
    supply_demand['CityName'].replace('Los Angeles-Long Beach-Anaheim', 'Los Angeles',inplace=True)
    supply_demand['CityName'].replace('Dallas-Fort Worth', 'Dallas',inplace=True)
    supply_demand['city_key'] = supply_demand.apply(lambda row: row['CityName'] + ' ' + row['StateName'], axis = 1)
    supply_demand = pd.merge(supply_demand,pop,how='inner', left_on = 'city_key', right_on = 'city')

    for d in dates:
        supply_demand [d] = supply_demand.apply(lambda row: (row[d+str('_for_sale')] - row[d+str('_sold')]), axis =1 )

    merged = pd.merge(supply_demand,zhvi,how='inner',left_on = 'CityName', right_on = 'RegionName', suffixes = ['_housing_surplus','_zhvi'])
    merged = merged[(merged['CityName'] == merged['RegionName_zhvi']) & (merged['StateName_housing_surplus'] == merged['StateName_zhvi'])]

    feature_list = ['2018-01-31_housing_surplus',
    '2018-02-28_housing_surplus',
    '2018-03-31_housing_surplus',
    '2018-04-30_housing_surplus',
    '2018-05-31_housing_surplus',
    '2018-06-30_housing_surplus',
    '2018-07-31_housing_surplus',
    '2018-08-31_housing_surplus',
    '2018-09-30_housing_surplus',
    '2018-10-31_housing_surplus',
    '2018-11-30_housing_surplus',
    '2018-12-31_housing_surplus',
    '2019-01-31_housing_surplus',
    '2019-02-28_housing_surplus',
    '2019-03-31_housing_surplus',
    '2019-04-30_housing_surplus',
    '2019-05-31_housing_surplus',
    '2019-06-30_housing_surplus',
    '2019-07-31_housing_surplus',
    '2019-08-31_housing_surplus',
    '2019-09-30_housing_surplus',
    '2019-10-31_housing_surplus',
    '2019-11-30_housing_surplus',
    '2019-12-31_housing_surplus',
    '2020-01-31_housing_surplus',
    '2020-02-29_housing_surplus',
    '2020-03-31_housing_surplus',
    '2020-04-30_housing_surplus',
    '2020-05-31_housing_surplus',
    '2020-06-30_housing_surplus',
    '2020-07-31_housing_surplus',
    '2020-08-31_housing_surplus',
    '2020-09-30_housing_surplus',
    '2020-10-31_housing_surplus',
    '2020-11-30_housing_surplus',
    '2020-12-31_housing_surplus',
    '2021-01-31_housing_surplus',
    '2021-02-28_housing_surplus',
    '2021-03-31_housing_surplus', 
    '2018-01-31_zhvi',
    '2018-02-28_zhvi',
    '2018-03-31_zhvi',
    '2018-04-30_zhvi',
    '2018-05-31_zhvi',
    '2018-06-30_zhvi',
    '2018-07-31_zhvi',
    '2018-08-31_zhvi',
    '2018-09-30_zhvi',
    '2018-10-31_zhvi',
    '2018-11-30_zhvi',
    '2018-12-31_zhvi',
    '2019-01-31_zhvi',
    '2019-02-28_zhvi',
    '2019-03-31_zhvi',
    '2019-04-30_zhvi',
    '2019-05-31_zhvi',
    '2019-06-30_zhvi',
    '2019-07-31_zhvi',
    '2019-08-31_zhvi',
    '2019-09-30_zhvi',
    '2019-10-31_zhvi',
    '2019-11-30_zhvi',
    '2019-12-31_zhvi',
    '2020-01-31_zhvi',
    '2020-02-29_zhvi',
    '2020-03-31_zhvi',
    '2020-04-30_zhvi',
    '2020-05-31_zhvi',
    '2020-06-30_zhvi',
    '2020-07-31_zhvi',
    '2020-08-31_zhvi',
    '2020-09-30_zhvi',
    '2020-10-31_zhvi',
    '2020-11-30_zhvi',
    '2020-12-31_zhvi',
    '2021-01-31_zhvi',
    '2021-02-28_zhvi',
    '2021-03-31_zhvi', 'netmig','npopchg_']
    labels = ['CityName','StateName_zhvi']

    clustering_df = merged[labels + feature_list]
    clustering_df['Name'] = clustering_df.apply(lambda row: row['CityName']+', '+ row['StateName_zhvi'], axis = 1)
    clustering_df.drop(labels,axis = 1, inplace=True)

    exp_clu101 = setup(clustering_df, normalize = True, numeric_features = feature_list, ignore_features = ['Name'], session_id = 123)
    kmeans = create_model('kmeans')

    kmean_results = assign_model(kmeans)
    kmean_results.sort_values('Cluster')

    plot_model(kmeans,'elbow')
    plot_model(kmeans, feature = 'Name', label = False)
    plot_model(kmeans,'silhouette')
    plot_model(kmeans,'tsne', feature = 'Name', label = True)
    plot_model(kmeans, plot = 'distribution')

    kmeans = create_model('kmeans', num_clusters = 2)
    kmean_results = assign_model(kmeans)
    plot_model(kmeans,'silhouette')

    kmeans = create_model('kmeans')
    kmean_results = assign_model(kmeans)
    kmean_results = kmean_results.sort_values('Cluster')

    plot_model(kmeans, plot = 'distribution', feature = 'npopchg_')

    df_line = pd.DataFrame()
    df_line['Year'] = []
    df_line['Home Value Index'] = []
    title_str = 'Pending Home Sale History in ' + city_str
    fig_2 = px.line(df_line, x="Year", y="Home Value Index", title=title_str)

    return container, fig, fig_2
# ------------------------------------------------------------------------------

app.layout = update_page_layout

# Interactive callbacks

#Given an input(year) update the output page components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='choropleth_graph', component_property='figure'),
     Output(component_id='line_graph', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'), 
     Input(component_id='slct_state', component_property='value'), 
     Input(component_id='slct_dataset', component_property='value'),
     Input(component_id='slct_view', component_property='value'),
     Input(component_id='slct_sale', component_property='value')]
)

def update_graph(selected_year, state_str, selected_dataset, selected_view, selected_sale):

    if selected_dataset == 'FMAC':
        return page_1(selected_year, state_str)
    elif selected_dataset == 'ZHVI':
        if selected_view == 'States':
            return page_2(selected_year, state_str)
        elif selected_view == 'Counties':
            return page_3(selected_year, state_str)
        elif selected_view == 'Cities':
            return page_4(selected_year, state_str)
    elif selected_dataset == 'ZORI':
        return page_5(selected_year, state_str)
    elif selected_dataset == 'SALES':
        if selected_sale == 'for_sale':
            return page_6(selected_year, state_str)
        if selected_sale == 'pending':
            return page_7(selected_year, state_str)
        if selected_sale == 'sale_speed':
            return page_8(selected_year, state_str)
        if selected_sale == 'sold':
            return page_9(selected_year, state_str)
    elif selected_dataset == 'FORECAST':
        return page_10(selected_year, state_str)
    elif selected_dataset == 'CLUSTER':
        return page_11(selected_year, state_str)
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)