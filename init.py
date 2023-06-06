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
#     cmsyscode=6
#     fromdate='04-May-2023'
#     todate='05-Jun-2023'
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("EXEC DemoData @cmsyscode= ?,@fromdate= ?,@todate= ?", (cmsyscode,fromdate,todate))  
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()


    fig = make_subplots(rows=1, cols=2, vertical_spacing=0.1, subplot_titles=(
        'Lead Status','Lead Source',
    ))
    T1 = go.Histogram(x=df['ls_description'],marker_color='#0bb4c6')
    T1.name = ''                                           # remove trace name display
    T1.showlegend=False                                   #to remove trace colour box
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(
        height=370, 
        width=1330 ,
         margin=dict(l=50, r=50, t=100, b=100) 
    )
    T2 = go.Histogram(x=df['COL_ContactLabel'],marker_color='#8BC34A')
    T2.name=''
    T2.showlegend=False
    fig.add_trace(T2,row=1,col=2)

    # fig.set_xticklabels(fig.get_xticklabels(), rotation=0, ha='right')
    xaxis_labels = df['COL_ContactLabel'].unique()

# Modify the x-axis labels
    # modified_labels = []
    # for i in xaxis_labels:
    #     if ' ' in i:
    #         label_parts = i.split(' ')
    #         modified_labels.append('<br>'.join(label_parts))
    #     else:
    #          modified_labels.append(i)

    #     xaxis_label = '<br>'.join(modified_labels)


      
    fig.update_layout(
        height=370, width=1350,
        margin=dict(l=50, r=50, t=50, b=50),
            plot_bgcolor='white',
            # paper_bgcolor='white', 
            bargap=0.2, 
            showlegend=False,
            # xaxis2=dict(title=xaxis_label)         
    )

    fig_dict = fig.to_dict()
    fig_dict['data'][0]['x'] = fig_dict['data'][0]['x'].tolist()
    fig_dict['data'][1]['x'] = fig_dict['data'][1]['x'].tolist()

    # fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn') potly gives whole inbuild header 

    #if we want some specific functions from inbuild header
    fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn', config={'modeBarButtonsToRemove': ['zoom2d','autoscale2d','pan2d','lasso2d','resetScale2d'],'displaylogo':False,'showlegend':False})
    return fig_html 

    # response = {'data': fig_dict}
    # return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

