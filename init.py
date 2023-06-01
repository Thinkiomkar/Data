from flask import Flask
import pyodbc
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as py
from plotly.tools import make_subplots

server = 'ttplsqleu.database.windows.net'
database = 'rms_live'
username = 'ttplsqladmineu'
password = 'TTPL@123'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

app = Flask(__name__)
@app.route('/', methods=['GET'])
def main():
    cmsyscode = 6
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("EXEC DemoData @cmsyscode=?", (cmsyscode,))  
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df = pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()

    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.1, subplot_titles=(
        'Leads Status',
    ))
    T1 = go.Histogram(x=df['ls_description'])
    T1.name = 'Leads Status'
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(
        height=500, 
        width=1200   
    )
    fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn')
    fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn', config={'displayModeBar': False})
    return fig_html 

if __name__ == '__main__':
    app.run(debug=True)

