import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from statistics import mean

app = dash.Dash(__name__)
server = app.server

#load data
first_run = True
state_idx = 0
df = pd.read_csv("FMAC-HPI.csv")
states = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']
main_dict = dict()

for state in states:
    group_by_date = dict()
    for index, row in df.iterrows():
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

    main_dict[state] = group_by_date



# choropleth map
app.layout = html.Div([

    html.H1("The Effects COVID-19 has on House Index Prices", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "1975", "value": 1975},
                     {"label": "1976", "value": 1976},
                     {"label": "1977", "value": 1977},
                     {"label": "1978", "value": 1978},
                     {"label": "1979", "value": 1979},
                     {"label": "1980", "value": 1980},
                     {"label": "1981", "value": 1981},
                     {"label": "1982", "value": 1982},
                     {"label": "1983", "value": 1983},
                     {"label": "1984", "value": 1984},
                     {"label": "1985", "value": 1985},
                     {"label": "1986", "value": 1986},
                     {"label": "1987", "value": 1987},
                     {"label": "1988", "value": 1988},
                     {"label": "1989", "value": 1989},
                     {"label": "1990", "value": 1990},
                     {"label": "1991", "value": 1991},
                     {"label": "1992", "value": 1992},
                     {"label": "1993", "value": 1993},
                     {"label": "1994", "value": 1994},
                     {"label": "1995", "value": 1995},
                     {"label": "1996", "value": 1996},
                     {"label": "1997", "value": 1997},
                     {"label": "1998", "value": 1998},
                     {"label": "1999", "value": 1999},
                     {"label": "2000", "value": 2000},
                     {"label": "2001", "value": 2001},
                     {"label": "2002", "value": 2002},
                     {"label": "2003", "value": 2003},
                     {"label": "2004", "value": 2004},
                     {"label": "2005", "value": 2005},
                     {"label": "2006", "value": 2006},
                     {"label": "2007", "value": 2007},
                     {"label": "2008", "value": 2008},
                     {"label": "2009", "value": 2009},
                     {"label": "2010", "value": 2010},
                     {"label": "2011", "value": 2011},
                     {"label": "2012", "value": 2012},
                     {"label": "2013", "value": 2013},
                     {"label": "2014", "value": 2014},
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017}],
                 multi=False,
                 value=2009,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_graph', figure={})

])



# ------------------------------------------------------------------------------
# Interactive callbacks

#Given an input(year) update the output page components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_graph', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(selected_year):

    container = ""
    dff = pd.DataFrame()
    state_code_arr = []
    hpi_arr = []
    for key in main_dict:
        selected_state = main_dict[key]
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
        color_continuous_scale=px.colors.sequential.YlGnBu,
        labels={'Housing Price Index': 'Housing Price Index'},
        template='plotly_dark'
    )
 
    #returns to the [output, output,....] in @app.callback()
    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)