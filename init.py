	
	
	
from flask import Flask, jsonify,request
import pyodbc
import pandas as pd
import plotly.offline as py
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
    cmsyscode =int(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    # cmsyscode=6
    # fromdate='04-May-2023'
    # todate='05-Jun-2023'
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("EXEC DemoData @cmsyscode= ?,@fromdate= ?,@todate= ?", (cmsyscode,fromdate,todate))  
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()


    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1, subplot_titles=(
        'Leads Status','Lead Source'
    ))
    T1 = go.Histogram(x=df['ls_description'])
    T1.name = 'Leads Status'
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(
        height=800, 
        width=1000  
    )

    T2 = go.Histogram(x=df['COL_ContactLabel'],)
    T2.name='Lead Source'
    fig.add_trace(T2,row=2,col=1)
    T2=go.histogram.Marker(color="blue")
    fig.update_layout(
        height=800, width=1000,
        margin=dict(l=50, r=50, t=100, b=100) ,paper_bgcolor="LightSteelBlue"  
        # legend_tracegroupgap=10,
        # legend_font_color="black",
        # legend_font_size=10
    )

    fig_dict = fig.to_dict()
    fig_dict['data'][0]['x'] = fig_dict['data'][0]['x'].tolist()
    fig_dict['data'][1]['x'] = fig_dict['data'][1]['x'].tolist()

    # fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn')
    # fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn', config={'displayModeBar': False})
    # return fig_html 

    response = {'data': fig_dict}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)


