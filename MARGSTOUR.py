from flask import Flask, request, jsonify
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Flask app for the backend
server = Flask(__name__)

# Shared data storage
data = pd.DataFrame(columns=[
    "Bar",
    "Margarita Rating",
    "Price Rating",
    "Atmosphere Rating",
    "Average Rating", 
    "Comments"
])

@server.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'GET':
        # Serve an HTML form
        return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Margarita Tour Submission</title>
            </head>
            <body>
                <h1>Submit Your Margarita Ratings</h1>
                <form method="post">
                    <label for="bar">Bar Name:</label><br>
                    <select id="bar" name="bar" required>
                        <option value="">Select a bar</option>
                        <option value="3 Needs">3 Needs</option>
                        <option value="Drink">Drink</option>
                        <option value="Orlandos">Orlandos</option>
                    </select><br><br>
                    
                    <label for="margarita_rating">Margarita Rating (1-10):</label><br>
                    <select id="margarita_rating" name="margarita_rating" required>
                        <option value="">Select a rating</option>
                        ''' + ''.join([f'<option value="{i}">{i}</option>' for i in range(1, 11)]) + '''
                    </select><br><br>

                    <label for="price_rating">Price Rating (1-10):</label><br>
                    <select id="price_rating" name="price_rating" required>
                        <option value="">Select a rating</option>
                        ''' + ''.join([f'<option value="{i}">{i}</option>' for i in range(1, 11)]) + '''
                    </select><br><br>

                    <label for="atmosphere_rating">Atmosphere Rating (1-10):</label><br>
                    <select id="atmosphere_rating" name="atmosphere_rating" required>
                        <option value="">Select a rating</option>
                        ''' + ''.join([f'<option value="{i}">{i}</option>' for i in range(1, 11)]) + '''
                    </select><br><br>
                    
                    <label for="comments">Comments:</label><br>
                    <textarea id="comments" name="comments"></textarea><br><br>
                    
                    <button type="submit">Submit</button>
                </form>
            </body>
            </html>
        '''
    elif request.method == 'POST':
        # Process the submitted data
        bar = request.form.get("bar")
        margarita_rating = float(request.form.get("margarita_rating"))
        price_rating = float(request.form.get("price_rating"))
        atmosphere_rating = float(request.form.get("atmosphere_rating"))
        comments = request.form.get("comments")

        global data

        # Check if the bar already exists in the DataFrame
        if bar in data['Bar'].values:
            # Update existing bar's ratings
            existing_row = data[data['Bar'] == bar].iloc[0]
            existing_margarita_rating = existing_row['Margarita Rating']
            existing_price_rating = existing_row['Price Rating']
            existing_atmosphere_rating = existing_row['Atmosphere Rating']
            existing_count = existing_row.get('Rating Count', 1)  # Default to 1 if not present

            # Update the average ratings
            new_count = existing_count + 1
            updated_margarita_rating = (existing_margarita_rating * existing_count + margarita_rating) / new_count
            updated_price_rating = (existing_price_rating * existing_count + price_rating) / new_count
            updated_atmosphere_rating = (existing_atmosphere_rating * existing_count + atmosphere_rating) / new_count
            updated_average_rating = (updated_margarita_rating + updated_price_rating + updated_atmosphere_rating) / 3
            average_rating = (updated_margarita_rating + updated_price_rating + updated_atmosphere_rating) / 3

            # Update the DataFrame row
            data.loc[data['Bar'] == bar, 'Margarita Rating'] = updated_margarita_rating
            data.loc[data['Bar'] == bar, 'Price Rating'] = updated_price_rating
            data.loc[data['Bar'] == bar, 'Atmosphere Rating'] = updated_atmosphere_rating
            data.loc[data['Bar'] == bar, 'Average Rating'] = updated_average_rating
            data.loc[data['Bar'] == bar, 'Rating Count'] = new_count
        else:
            # Add a new entry for the bar
            average_rating = (margarita_rating + price_rating + atmosphere_rating) / 3
            new_entry = {
                "Bar": bar,
                "Margarita Rating": margarita_rating,
                "Price Rating": price_rating,
                "Atmosphere Rating": atmosphere_rating,
                "Average Rating": average_rating,
                "Rating Count": 1,
                "Comments": comments
            }
            data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)

        print(data)  # For debugging: confirm that the data updates correctly
        
        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Thank You!</title>
            </head>
            <body>
                <h1>Thank you for your submission!</h1>
                <p>Bar: {bar}, Margarita Rating: {margarita_rating}, Price Rating: {price_rating}, Atmosphere Rating: {atmosphere_rating}, Average Rating: {average_rating:.2f}</p>
                <button onclick="window.location.href='/submit'">Create New Submission</button>
            </body>
            </html>
        """


# Dash app for the frontend
app = Dash(__name__, server=server, url_base_pathname='/dashboard/')

app.layout = html.Div([
    html.H1("Margarita Tour Dashboard"),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    global data
    if data.empty:
        return go.Figure().add_trace(go.Scatter(x=[], y=[], mode='text', text=["No Data Yet!"]))

    # Ensure the 'Bar' column is treated as a category
    data['Bar'] = data['Bar'].astype('category')

    # Define a consistent color map for each unique Bar value
    unique_bars = data['Bar'].unique()
    color_map = {
        bar: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
        for i, bar in enumerate(unique_bars)
    }

    # Create subplots with more vertical spacing
    fig = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=(
            "Margarita Ratings", "Price Ratings", "Atmosphere Ratings", "Average Ratings"
        ),
        vertical_spacing=0.1
    )

    # Add separate traces for each unique Bar for each rating type
    for bar in unique_bars:
        filtered_data = data[data['Bar'] == bar]
        color = color_map[bar]

        # Margarita Rating trace
        fig.add_trace(
            go.Bar(
                x=filtered_data['Bar'],
                y=filtered_data['Margarita Rating'],
                marker_color=color,
                name=bar
            ),
            row=1, col=1
        )
        
        # Price Rating trace
        fig.add_trace(
            go.Bar(
                x=filtered_data['Bar'],
                y=filtered_data['Price Rating'],
                marker_color=color,
                showlegend=False  # Show the legend only in the first subplot
            ),
            row=2, col=1
        )
        
        # Atmosphere Rating trace
        fig.add_trace(
            go.Bar(
                x=filtered_data['Bar'],
                y=filtered_data['Atmosphere Rating'],
                marker_color=color,
                showlegend=False  # Show the legend only in the first subplot
            ),
            row=3, col=1
        )
        
        # Average Rating trace
        fig.add_trace(
            go.Bar(
                x=filtered_data['Bar'],
                y=filtered_data['Average Rating'],
                marker_color=color,
                showlegend=False  # Show the legend only in the first subplot
            ),
            row=4, col=1
        )

    # Update y-axis settings for all subplots
    for i in range(1, 5):  # Iterate through rows 1 to 4
        fig.update_yaxes(
            range=[0, 10],  # Set y-axis range
            tickmode="linear",  # Show ticks at regular intervals
            dtick=1,  # Interval between ticks
            showgrid=True,  # Show grid lines
            gridcolor="lightgrey",  # Optional: Set grid line color
            row=i, col=1
        )


    # Update layout for a cleaner look
    fig.update_layout(
        showlegend=True,  # Ensure the legend is shown
        margin=dict(t=50, b=50, r=50),
        height=1200
    )

    return fig

if __name__ == "__main__":
    server.run(debug=True, port=8050)