import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

dfa = pd.read_excel("Rental_Averages.xlsx")

year_val = []
for key, column in dfa.iteritems():
    try:
        int_v = int(key)
    except ValueError:
        continue
    year_val.append(int_v)

main_dict = {}
for index, row in dfa.iterrows():
    values = row.values
    state_name = values[1]
    cur_vals = values[2:]
    if state_name not in main_dict.keys():
        main_dict[state_name] = {}
        for i, year in enumerate(year_val, 0):
            if year not in main_dict[state_name].keys():
                main_dict[state_name][year] = {}
            main_dict[state_name][year] = cur_vals[i]

print(main_dict)


app.layout = html.Div([

    html.H1("Rental prices from years 1996 to 2021", style={'text-align': 'center'}),

    dcc.Dropdown(id="select_year",
                 options=[
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
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018},
                     {"label": "2019", "value": 2019},
                     {"label": "2020", "value": 2020},
                     {"label": "2021", "value": 2021}],
                 multi=False,
                 value=1996,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_graph', figure={})

])


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_graph', component_property='figure')],
    [Input(component_id='select_year', component_property='value')]
)
def update_graph(select_year):
    container = "The year selected by user was: {}".format(select_year)

    hover_arr = []
    state_arr = []

    for state_name_key, avg_values in main_dict.items():
        selected_avg = avg_values[select_year]

        state_arr.append(state_name_key)
        hover_arr.append(selected_avg)

    dfa['state_code'] = state_arr
    dfa['Rental Avg'] = hover_arr

    fig = px.choropleth(
        data_frame=dfa,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='Rental Avg',
        hover_data=['state_code', 'Rental Avg'],
        color_continuous_scale=px.colors.sequential.YlGnBu,
        labels={'Rental Avg': 'Rental Avg'},
        template='plotly_dark'
    )
    return container, fig


if __name__ == '__main__':
    app.run_server(debug=True)
