from flask import Flask, jsonify
import pyodbc
import pandas as pd
import plotly.graph_objects as go
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
    json_data = df.to_json(orient='split')
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
    fig.to_dict()['data'][0]['x'] =fig.to_dict()['data'][0]['x'].tolist()
  
    return jsonify({'data': json_data})

if __name__ == '__main__':
    app.run(debug=True)


