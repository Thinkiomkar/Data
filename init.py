from flask import Flask
from plotly import tools
import plotly.offline as py
import plotly.graph_objs as go
import pyodbc
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp


import plotly.express as px
from plotly.subplots import make_subplots


server = 'ttplsqleu.database.windows.net'
database = 'rms_live'
username = 'ttplsqladmineu'
password = 'TTPL@123'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    cmsyscode = 6  # Set the cmsyscode parameter to 6

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
    fig = sp.make_subplots(rows=6, cols=1, vertical_spacing=0.08, subplot_titles=(
        'Leads From Sources',
        'Leads Status',
        'Leads Counts and Status',
        'Leads Counts and Status'
    ))

    # top_40 = df.nlargest(40, 'com_firstname_numeric')

    # fig.add_trace(
    #     go.Scatter(x=top_40['com_firstname'], y=top_40['COL_ContactLabel'], mode='markers'),
    #     row=1, col=1
    # )

    fig.add_trace(
        go.Histogram(x=df['COL_ContactLabel']),
        row=2, col=1
    )

    fig.add_trace(
        go.Histogram(x=df['ls_description']),
        row=3, col=1
    )

    # fig.add_trace(
    #     go.Bar(x=df['COL_ContactLabel'], y=df['ls_description']),
    #     row=4, col=1
    # )

    colors = {
    'Category1': 'blue',
    'Category2': 'green',
    'Category3': 'red',
    # Add more categories and colors as needed
     }

    fig.add_trace(
    go.Bar(x=df['COL_ContactLabel'], y=df['ls_description'], marker=dict(color=[colors.get(category,'blue') for category in df['ls_description']])),
    row=4, col=1
      )
    
    fig.add_trace(
        go.Histogram(y=df['COL_ContactLabel'], histfunc='count'),
        row=5, col=1
    )





 #Pie diagram
    # count_df = df['ls_description'].value_counts().reset_index()
    # count_df.columns = ['ls_description', 'count']
    # df_merged = df.merge(count_df, on='ls_description')
    # trace1 = go.Pie(df_merged, names='ls_description', values='count',
    #          title='Percentage of leads',
    #          hover_data=['ls_description', 'count'],
    #          labels={'ls_description': 'Lead Status', 'count': 'Count'})


    # layout = go.Layout(title="Global Emissions 1990-2011",)
    # data = [trace1]
    # fig = go.Figure(data=data, layout=layout)
    # py.plot(fig, filename='simple-pie-subplot')



    fig.update_layout(height=5000, width=1200, showlegend=False)

    # Convert figure to HTML string
    fig_html = fig.to_html(full_html=False)

    # Return the HTML string
    return fig_html

if __name__ == '__main__':
    app.run(debug=True)


