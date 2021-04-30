import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from statistics import mean

app = dash.Dash(__name__)
states = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']

#Load Data - Quandl, Freddie Mac Housing Price Index
state_idx = 0
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



# choropleth map
app.layout = html.Div([
    html.H1("The Effect of COVID-19 on Housing Index Prices in the US", style={'text-align': 'center'}),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='choropleth_graph', figure={}),
    dcc.Slider(id="slct_year", min=1975, max=2017, step=1, value=2008,
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
            2017: "2017"
        }
    ),
    dcc.Graph(id='line_graph', children=[]),
    html.I("Enter State Code"),
    html.Br(),
    dcc.Input(
        id="slct_state",
        type='text',
        value='AZ'
    )
])



# ------------------------------------------------------------------------------
# Interactive callbacks

#Given an input(year) update the output page components

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='choropleth_graph', component_property='figure'),
     Output(component_id='line_graph', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'), Input(component_id='slct_state', component_property='value')]
)

def update_graph(selected_year, state_str):

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
    my_color_scale = ["yellow", "orange", "red", "pink", "purple", "#19D3F3", "blue", "#00CC96", "green", "#16FF32"]

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


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
