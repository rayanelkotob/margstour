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
    "Average Rating"
])

@server.route('/home')
def homepage():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Margarita Tour</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Lilita+One&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Lilita One', sans-serif;
                margin: 0;
                padding: 0;
                background-color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
            }

            img {
                max-width: 90%;
                height: auto;
                margin-bottom: 20px;
                border-radius: 8px;
            }

            .button {
                width: 90%;
                max-width: 400px;
                font-size: 1.2em;
                color: white;
                background-color: #abd148;
                padding: 10px;
                margin-bottom: 15px;
                text-decoration: none;
                border: none;
                box-sizing: border-box;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                text-align: center; /* Center text in the button */
                display: block; /* Ensure button spans full width */
            }

            .button:hover {
                background-color: #86a338;
            }
        </style>
    </head>
    <body>
        <img src="static/margs-crawl-home.jpeg" alt="Margarita Tour Image">
        <a href="/submit" class="button">SUBMIT RATING</a>
        <a href="/dashboard" class="button">GO TO DASHBOARD</a>
    </body>
    </html>
    """

@server.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'GET':
        # Serve an HTML form
        return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Margarita Tour Submission</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://fonts.googleapis.com/css2?family=Lilita+One&display=swap" rel="stylesheet">
                <style>
                     body {
                        font-family: 'Lilita One', sans-serif;
                        margin: 0;
                        padding: 0;
                    }

                    form {
                        max-width: 400px;
                        margin: 20px auto;
                        padding: 20px;
                        border-radius: none;
                        background-color: white;
                        box-shadow: none;
                    }

                    label {
                        font-size: 1.2em;
                        margin-bottom: 8px;
                        display: block;
                    }

                    input, select, textarea, button {
                        width: 100%;
                        max-width: 100%;
                        padding: 10px;
                        margin-bottom: 15px;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                    }

                    textarea {
                        resize: none;
                        width: 100%;
                        max-width: 100%;
                    }

                    button {
                        background-color: #abd148;
                        color: white;
                        border: none;
                        font-size: 1.2em;
                        font-family: 'Lilita One', sans-serif;
                        cursor: pointer;
                        margin: 5px;
                    }

                    button:hover {
                        background-color: #86a338;
                    }
                </style>
            </head>
            <body>
                <h1 style="text-align: center;">SUBMIT YOUR MARGS RATING</h1>
                <form method="post">
                    <label for="bar">BAR NAME:</label>
                    <select id="bar" name="bar" required>
                        <option value="">Select a bar</option>
                        <option value="3 Needs">3 Needs</option>
                        <option value="Wallflower">Wallflower</option>
                        <option value="Archives">Archives</option>
                        <option value="Orlandos">Orlandos</option>
                        <option value="Drink">Drink</option>
                    </select>
                    
                    <label for="margarita_rating">MARG RATING (1-10):</label>
                    <select id="margarita_rating" name="margarita_rating" required>
                        <option value="">Select a rating</option>
                        <!-- Generate options dynamically -->
                        <script>
                            for (let i = 1; i <= 10; i++) {
                                document.write(`<option value="${i}">${i}</option>`);
                            }
                        </script>
                    </select>

                    <label for="price_rating">PRICE RATING (1-10):</label>
                    <select id="price_rating" name="price_rating" required>
                        <option value="">Select a rating</option>
                        <script>
                            for (let i = 1; i <= 10; i++) {
                                document.write(`<option value="${i}">${i}</option>`);
                            }
                        </script>
                    </select>

                    <label for="atmosphere_rating">ATMOSPHERE RATING (1-10):</label>
                    <select id="atmosphere_rating" name="atmosphere_rating" required>
                        <option value="">Select a rating</option>
                        <script>
                            for (let i = 1; i <= 10; i++) {
                                document.write(`<option value="${i}">${i}</option>`);
                            }
                        </script>
                    </select>

                    <button type="submit">SUBMIT</button>
                    <button type="button" onclick="window.location.href='/dashboard'">GO TO DASHBOARD</button>
                    <button type="button" onclick="window.location.href='/home'">GO TO HOMEPAGE</button>
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
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://fonts.googleapis.com/css2?family=Lilita+One&display=swap" rel="stylesheet">
                <style>
                    body {{
                        font-family: 'Lilita One', sans-serif;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background-color: white;
                    }}

                    .thank-you-container {{
                        max-width: 400px;
                        text-align: center;
                        padding: 20px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        border-radius: 8px;
                        background-color: white;
                        box-shadow: none;
                    }}

                    h1 {{
                        font-size: 1.8em;
                        margin-bottom: 20px;
                    }}

                    p {{
                        font-size: 1.2em;
                        margin-bottom: 20px;
                    }}

                    button {{
                        width: 100%;
                        font-size: 1.2em;
                        font-family: 'Lilita One', sans-serif;
                        margin: 5px auto;
                        padding: 10px;
                        background-color: #abd148;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }}

                    button:hover {{
                        background-color: #86a338;
                    }}
                </style>
            </head>
            <body>
                <div class="thank-you-container">
                    <h1>THANK YOUR FOR YOUR SUBMISSION!</h1>
                    <p><strong>BAR:</strong> {bar}</p>
                    <p><strong>MARG RATING:</strong> {margarita_rating}</p>
                    <p><strong>PRICE RATING:</strong> {price_rating}</p>
                    <p><strong>ATMOSPHERE RATING:</strong> {atmosphere_rating}</p>
                    <p><strong>AVERAGE RATING:</strong> {average_rating:.2f}</p>
                    <button onclick="window.location.href='/submit'">CREATE NEW SUBMISSION</button>
                    <button type="button" onclick="window.location.href='/dashboard'">GO TO DASHBOARD</button>
                    <button type="button" onclick="window.location.href='/home'">GO TO HOMEPAGE</button>
                </div>
            </body>
            </html>
        """

# Dash app for the frontend
app = Dash(
    __name__,
    server=server,
    url_base_pathname='/dashboard/',
    external_stylesheets=["https://fonts.googleapis.com/css2?family=Lilita+One&display=swap"]
)

# Define the layout
app.layout = html.Div(
    style={
        "font-family": "'Lilita One', sans-serif",  # Global font
        "background-color": "white",  # White background
        "padding": "0",  # No extra padding
        "margin": "0 auto",  # Center the content
        "text-align": "center"  # Align all content to the center
    },
    children=[
        html.H1(
            "MARGS TOUR DASHBOARD",
            style={
                "text-align": "center",  # Center the title
                "margin": "10px 0",  # Minimal vertical spacing
                "padding": "10px 0"  # Padding around the title
            }
        ),
        # Dynamic graph container
        html.Div(
            children=[
                dcc.Graph(
                    id='live-graph',
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=5 * 1000,  # Update every 5 seconds
                    n_intervals=0
                )
            ]
        ),
        # Add buttons at the bottom
         html.Div(
            style={"margin-top": "20px"},
            children=[
                html.A(
                    "GO TO SUBMISSION PAGE",
                    href="/submit",
                    style={
                        "display": "inline-block",
                        "background-color": "#abd148",
                        "color": "white",
                        "padding": "10px 20px",
                        "margin": "5px",
                        "text-decoration": "none",
                        "border-radius": "5px",
                        "font-size": "1.2em",
                        "font-family": "'Lilita One', sans-serif",
                        "cursor": "pointer",
                        "transition": "background-color 0.3s ease",
                        "width": "80%",
                    }
                ),
                html.A(
                    "GO TO HOMEPAGE",
                    href="/home",
                    style={
                        "display": "inline-block",
                        "background-color": "#abd148",
                        "color": "white",
                        "padding": "10px 20px",
                        "margin": "5px",
                        "text-decoration": "none",
                        "border-radius": "5px",
                        "font-size": "1.2em",
                        "font-family": "'Lilita One', sans-serif",
                        "cursor": "pointer",
                        "transition": "background-color 0.3s ease",
                        "width": "80%",
                    }
                ),
            ]
         )
    ]
)

# Callback for updating the graph
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
        subplot_titles=[
            "MARGS RATINGS", "PRICE RATINGS", "ATMOSPHERE RATINGS", "AVERAGE RATINGS"
        ],
        vertical_spacing=0.1  # Spacing between subplots
    )

    # Add separate traces for each unique Bar for each rating type
    for bar in unique_bars:
        filtered_data = data[data['Bar'] == bar]
        color = color_map[bar]

        # Add traces for different rating types
        fig.add_trace(
            go.Bar(x=filtered_data['Bar'], y=filtered_data['Margarita Rating'], marker_color=color, name=bar),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=filtered_data['Bar'], y=filtered_data['Price Rating'], marker_color=color, showlegend=False),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=filtered_data['Bar'], y=filtered_data['Atmosphere Rating'], marker_color=color, showlegend=False),
            row=3, col=1
        )
        fig.add_trace(
            go.Bar(x=filtered_data['Bar'], y=filtered_data['Average Rating'], marker_color=color, showlegend=False),
            row=4, col=1
        )

    # Update y-axis settings for all subplots
    for i in range(1, 5):  # Iterate through rows 1 to 4
        fig.update_yaxes(
            range=[0, 10],  # Set y-axis range
            tickmode="linear",  # Linear ticks
            dtick=1,  # Tick interval
            showgrid=True,  # Show grid lines
            gridcolor="lightgrey",  # Grid line color
            row=i, col=1
        )

    # Update layout for better responsiveness and spacing
    fig.update_layout(
        showlegend=False,
        margin=dict(t=30, b=30, l=10, r=10),  # Minimal margins for better fit
        height=1000,  # Adjust height for better display on all devices
        font={"family": "'Lilita One', sans-serif", "size": 16, "color": "black"}
    )

    return fig

if __name__ == "__main__":
    server.run(debug=True, host='0.0.0.0', port=8050)