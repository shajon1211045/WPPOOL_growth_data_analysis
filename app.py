import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load and prepare data
df = pd.read_csv('data_updated.csv', parse_dates=['install_date', 'last_active_date', 'pro_upgrade_date'])
df['month'] = df['install_date'].dt.to_period('M').astype(str)

# Visualization 1: Bar Chart for Revenue from Each Country by Month
# Group by month and country to calculate total revenue
revenue_by_country_month = df.groupby(['month', 'country'])['monthly_revenue'].sum().reset_index()

# Create the initial bar chart (no color by month)
fig1 = px.bar(revenue_by_country_month, 
              x='country', 
              y='monthly_revenue', 
              title='Revenue from Each Country Filtered by Month', 
              labels={'monthly_revenue': 'Total Revenue ($)', 'country': 'Country', 'month': 'Month'},
              height=600, 
              color='country')  # Use 'country' for different colors

# Format y-axis as currency
fig1.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")

# Visualization 2: User Acquisition Over Time
daily_installs = df.groupby('install_date')['user_id'].count().reset_index()
fig2 = px.line(daily_installs, 
              x='install_date', 
              y='user_id',
              title='Daily User Acquisition',
              labels={'user_id': 'New Users', 'install_date': 'Date'})

# Visualization 4: Activity vs Churn
fig4 = px.box(df, 
             x='churned', 
             y='days_active',
             title='Activity Duration vs Churn Status',
             labels={'churned': 'Churned', 'days_active': 'Days Active'},
             color='churned')

# Create Dash app
app = dash.Dash(__name__)

# Create Dropdown for Month filter (for revenue chart)
app.layout = html.Div([ 
    # Header with logo and title
    html.Div([
        html.Img(src='assets/wppool_logo.png', style={'height': '50px', 'width': 'auto', 'padding-right': '10px'}),
        html.H1("WPPOOL User Analytics Dashboard", style={'display': 'inline-block', 'vertical-align': 'middle'})
    ], style={'textAlign': 'center', 'padding': '20px'}),

    # Dashboard Layout with the Graphs
    html.Div([ 
        # Dropdown for Month Filter
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in revenue_by_country_month['month'].unique()],
            value=revenue_by_country_month['month'].unique()[0],  # Default to the first month
            style={'width': '300px', 'margin': '20px'}
        ),
        
        # Revenue chart for selected month
        dcc.Graph(id='revenue-chart', figure=fig1, className='six columns'),

        # Other Graphs
        dcc.Graph(figure=fig2, className='six columns'),
    ], className='row'),

    html.Div([
        # Dropdown to filter Free/Pro (Only for Map Chart)
        dcc.Dropdown(
            id='subscription-dropdown',
            options=[
                {'label': 'Free', 'value': 'Free'},
                {'label': 'Pro', 'value': 'Pro'},
            ],
            value='Free',  # Default value
            style={'width': '200px', 'margin': '20px'}
        ),
        dcc.Graph(id='country-map', className='six columns'),
        dcc.Graph(figure=fig4, className='six columns'),
    ], className='row')
])

@app.callback(
    Output('revenue-chart', 'figure'),
    Input('month-dropdown', 'value')  # Listen to month dropdown value
)
def update_revenue_chart(selected_month):
    # Filter data based on selected month
    filtered_data = revenue_by_country_month[revenue_by_country_month['month'] == selected_month]

    # Create the updated bar chart for the selected month with color by country
    fig1 = px.bar(filtered_data, 
                  x='country', 
                  y='monthly_revenue', 
                  title=f'Revenue from Each Country for {selected_month}', 
                  labels={'monthly_revenue': 'Total Revenue ($)', 'country': 'Country'},
                  height=600,
                  color='country')  # Color by country
    
    # Format y-axis as currency
    fig1.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")

    return fig1

@app.callback(
    Output('country-map', 'figure'),
    Input('subscription-dropdown', 'value')  # Listen to dropdown value
)
def update_map(subscription_type):
    # Filter data based on selected subscription type
    filtered_df = df[df['subscription_type'] == subscription_type]
    
    # Country-wise user distribution
    country_dist = filtered_df['country'].value_counts().reset_index()
    country_dist.columns = ['country', 'count']  # Rename columns to match expectations

    # Create choropleth map with updated columns
    fig3 = px.choropleth(country_dist,
                         locations='country',  # Use 'country' column for locations
                         locationmode='country names',
                         color='count',  # Use 'count' column for color
                         title=f'User Distribution by Country ({subscription_type} users)',
                         labels={'country': 'Country', 'count': 'Users'},
                         height=600)  # Set height for better visibility
    
    return fig3

# Run the app
server = app.server  # Required for deployment

if __name__ == '__main__':
    app.run_server( debug=True)
