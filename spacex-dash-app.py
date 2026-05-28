# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
# FIX: Updated the filename to the standard CSV dataset name
spacex_df = pd.read_csv("spacex_launch_dash.csv") 
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Dynamically generate the dropdown choices from the dataframe rows
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in spacex_df['Launch Site'].unique():
    dropdown_options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an integrated app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    # TASK 1: Dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart container displaying dynamic success shares
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: RangeSlider component for filtering launch records by payload mass
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0: '0 Kg',
            2500: '2500 Kg',
            5000: '5000 Kg',
            7500: '7500 Kg',
            10000: '10000 Kg'
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart container displaying mass/outcome correlations
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2 Callback: Renders the success-pie-chart based on selected site dropdown
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Group by 'class' and calculate frequency using a structural count holder
        site_counts = filtered_df.groupby('class').size().reset_index(name='count')
        
        fig = px.pie(
            site_counts,
            values='count',
            names='class',
            title=f'Total Success vs. Failed Launches for Site {entered_site}'
        )
        return fig

# TASK 4 Callback: Renders the success-payload-scatter-chart based on dropdown & slider
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    
    # Isolate records within selected slider weights using consistent column syntax
    payload_filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    if entered_site == 'ALL':
        fig = px.scatter(
            payload_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Launch Outcome (Success=1, Failure=0)'}
        )
        return fig
    else:
        site_payload_filtered_df = payload_filtered_df[
            payload_filtered_df['Launch Site'] == entered_site
        ]
        fig = px.scatter(
            site_payload_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for Site: {entered_site}',
            labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Launch Outcome (Success=1, Failure=0)'}
        )
        return fig


    # Run the app
if __name__ == '__main__':
    app.run(debug=True)