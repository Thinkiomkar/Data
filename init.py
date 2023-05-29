from flask import Flask, request, jsonify
import pyodbc
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import json

server = 'ttplsqleu.database.windows.net'
database = 'rms_live'
username = 'ttplsqladmineu'
password = 'TTPL@123'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    cmsyscode = request.args.get('cmsyscode')

    if not cmsyscode:
        return jsonify({'error': 'Missing required parameter: cmsyscode'}), 400

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    cursor.execute("EXEC DemoData @cmsyscode=?", (cmsyscode,))   #calling procedures that I made in SQL

    result = cursor.fetchall() #fetching data of particular ID

    columns = [column[0] for column in cursor.description]

    result_reshaped = [tuple(row) for row in result]

    df = pd.DataFrame(result_reshaped, columns=columns)

    cursor.close()
    conn.close()

    # Create visualizations using plotly
    fig = sp.make_subplots(rows=5, cols=1, vertical_spacing=0.5, subplot_titles=(
        'Leads and Sources Relationship',
        'Leads From Sources',
        'Leads Status',
        'Leads Counts and Status',
        'Leads Counts and Status'
    ))

    top_40 = df.nlargest(40, 'com_firstname_numeric')

    fig.add_trace(
        go.Scatter(x=top_40['com_firstname'], y=top_40['COL_ContactLabel'], mode='markers'),
        row=1, col=1
    )

    fig.add_trace(
        go.Histogram(x=df['COL_ContactLabel']),
        row=2, col=1
    )

    fig.add_trace(
        go.Histogram(x=df['ls_description']),
        row=3, col=1
    )

    fig.add_trace(
        go.Bar(x=df['COL_ContactLabel'], y=df['ls_description'], barmode='stack'),
        row=4, col=1
    )

    fig.add_trace(
        go.Histogram(y=df['COL_ContactLabel'], histfunc='count', barmode='stack', ybins=dict(size=1)),
        row=5, col=1
    )

    fig.update_layout(height=800, width=600, showlegend=False)

    # Convert the plotly figure to JSON
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Return the JSON representation of the figure
    return jsonify({'body': fig_json})

if __name__ == '__main__':
    app.run(debug=True)
