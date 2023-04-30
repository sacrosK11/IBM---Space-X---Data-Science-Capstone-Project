import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Dropdown list(s)
launch_site_list = []
launch_site_list.append('ALL')
for index, row in spacex_df['Launch Site'].value_counts().to_frame().iterrows():
    launch_site_list.append(row.name)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                    options=[{'label': i, 'value': i} for i in launch_site_list],
                                    style={'width':'100%', 'padding':'3px', 'font-size': '20px', 'text-align-last': 'left'},
                                    value='ALL'),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=min_payload, max=max_payload, step=1000, value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df[['Launch Site', 'class']].groupby(by=['Launch Site'], as_index=False).mean()
        fig = px.pie(filtered_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches by Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[['Launch Site', 'class']][spacex_df['Launch Site'] == entered_site]
        mean = filtered_df.groupby(by='Launch Site', as_index=False).mean()
        means = {}
        means[1] = mean['class'][0]
        means[0] = 1 - means[1]
        fig = px.pie(values=means.values(), names=means.keys(),
                     title=f'Total Success Launches by Site: {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])

def get_scatter_plot(entered_site, payload_range):
    # print('min:', payload_range[0], '\tmax:', payload_range[1])
    # print(entered_site)
    if entered_site == 'ALL':
        payload_filtered_df = spacex_df[['Payload Mass (kg)', 'Booster Version Category', 'Launch Site', 'class']][(spacex_df['Payload Mass (kg)'] <= payload_range[1]) & (spacex_df['Payload Mass (kg)'] >= payload_range[0])]
    else:
        payload_filtered_df = spacex_df[['Payload Mass (kg)', 'Booster Version Category', 'Launch Site', 'class']][(spacex_df['Payload Mass (kg)'] <= payload_range[1]) &
                                                                                                                   (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                                                                                                   (spacex_df['Launch Site'] == entered_site)]
    fig = px.scatter(data_frame=payload_filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

