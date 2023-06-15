from flask import Flask, jsonify,request
import pyodbc
import pandas as pd
import numpy as np
import plotly.offline as py
import plotly.graph_objects as go
from plotly.tools import make_subplots
import plotly.express as px
import config
import json

connection_string = config.SQL_CONNECTION_STRING
app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    cmsyscode =str(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor() 
    cursor.execute("EXEC DemoData @cmsyscode= ?,@fromdate= ?,@todate= ?", (cmsyscode,fromdate,todate))   
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()
    fig = make_subplots(rows=2, cols=2, vertical_spacing=0.15, subplot_titles=(
        'Lead Status','Lead Source','Lead Count & Status'
    ))
    T1 = go.Histogram(x=df['ls_description'],marker_color='#0bb4c6')
    T1.name = ''                                                                        
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(
        height=400, 
        width=1330 ,
        margin=dict(l=50, r=50, t=100, b=100) 
    )
    T2 = go.Histogram(x=df['COL_ContactLabel'],marker_color='#8BC34A')
    T2.name=''
    fig.add_trace(T2,row=1,col=2)
    xaxis_labels =df['COL_ContactLabel'].unique()
    updated_labels = []
    for label in xaxis_labels:
        if ' ' in label:
            label_parts = label.split(' ')
            updated_labels.append('<br>'.join(label_parts))
        else:
            updated_labels.append(label)            
    fig.update_layout(
        height=600, width=1350,#h=400 
        margin=dict(l=50, r=50, t=50, b=50),
            plot_bgcolor='white', 
            bargap=0.2, 
            showlegend=False, 
            xaxis2=dict(
            tickmode='array',
            tickvals=list(range(0, len(updated_labels)+1)),
            ticktext=updated_labels,
            showticklabels=True,
            tickfont=dict(size=12),
            automargin=True,)  
    )
    fig.update_annotations(font_size=20)
    fig_dict = fig.to_dict()
    fig_dict['data'][0]['x'] = fig_dict['data'][0]['x'].tolist()
    fig_dict['data'][1]['x'] = fig_dict['data'][1]['x'].tolist()
    response = {'data': fig_dict,'config': {'modeBarButtonsToRemove': ['zoom2d', 'autoscale2d', 'pan2d', 'lasso2d', 'resetScale2d'], 'displaylogo': False}}
    response_json = json.dumps(response)
    return jsonify(response_json)

@app.route('/line', methods=['GET'])
def main3():
    cmsyscode =str(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor() 
    cursor.execute("EXEC DemoData @cmsyscode= ?,@fromdate= ?,@todate= ?", (cmsyscode,fromdate,todate))   
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()
    fig = make_subplots(rows=3, cols=1, vertical_spacing=0.15, subplot_titles=(
        'Lead Status',
    ))
    counts = df.groupby(['COL_ContactLabel', 'ls_description']).size().reset_index(name='count')
    fig = px.bar(counts, x='COL_ContactLabel', y='count', color='ls_description', 
             title=' % Of  Leads Conversions From Sources', barmode='group', text_auto='ls_description')
    fig.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis=dict(title='Sources'),
                  yaxis=dict(title='Total'),
                  legend=dict(title='Lead Status'))  
    fig_json=fig.to_json()
    response = {'data': fig_json,'config': {'modeBarButtonsToRemove': ['zoom2d', 'autoscale2d', 'pan2d', 'lasso2d', 'resetScale2d'], 'displaylogo': False}}
    response_json = json.dumps(response)
    return jsonify(response_json)

if __name__ == '__main__':
    app.run(debug=True)
