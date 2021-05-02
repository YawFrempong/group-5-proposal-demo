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
    cur_row = values[2:]
    if state_name not in main_dict.keys():
        main_dict[state_name] = {}
        for i, year in enumerate(year_val, 0):
            if year not in main_dict[state_name].keys():
                main_dict[state_name][year] = {}
            main_dict[state_name][year] = cur_row[i]

options_list = []
for year in year_val:
    options_list.append({"label": str(year), "value": year})


app.layout = html.Div([

    html.H1("Rental prices from years "+str(year_val[0])+" to " + str(year_val[-1]), style={'text-align': 'center'}),

    dcc.Dropdown(id="select_year",
                 options=options_list,
                 multi=False,
                 value=year_val[0],
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
