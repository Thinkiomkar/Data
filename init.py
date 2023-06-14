from flask import Flask, jsonify,request
import pyodbc
import pandas as pd
import numpy as np
import plotly.offline as py
import plotly.graph_objects as go
from plotly.tools import make_subplots
import plotly.subplots as sp
import plotly.express as px
import config

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
    T1.name = ''                                           # remove trace name display
    # T1.showlegend=False                                   #to remove trace colour box
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(
        height=400, 
        width=1330 ,
        margin=dict(l=50, r=50, t=100, b=100) 
    )
    T2 = go.Histogram(x=df['COL_ContactLabel'],marker_color='#8BC34A')
    T2.name=''
    # T2.showlegend=False
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
            # paper_bgcolor='white', 
            bargap=0.2, 
            showlegend=False,
            # xaxis2=dict(title=xaxis_label) 
            xaxis2=dict(
            tickmode='array',
            tickvals=list(range(0, len(updated_labels)+1)),
            ticktext=updated_labels,
            showticklabels=True,
            tickfont=dict(size=12),
            automargin=True,  
    )  
    )
    fig.update_annotations(font_size=20)  #increase title size of plot    
    fig_dict = fig.to_dict()
    fig_dict['data'][0]['x'] = fig_dict['data'][0]['x'].tolist()
    fig_dict['data'][1]['x'] = fig_dict['data'][1]['x'].tolist()
    response = {'data': fig_dict}
    return jsonify(response)

@app.route('/pie1', methods=['GET'])
def main1():
    cmsyscode =str(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    um_user_syscode=str(request.args.get('um_user_syscode'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("EXEC LeadStatus_Graph_PY  @CM_syscode= ?,@fromdate= ?,@todate= ?,@um_user_syscode= ?", (cmsyscode,fromdate,todate,um_user_syscode))   
    cursor.execute('''SELECT * FROM rms_live.TempLeadGraphTablePY WHERE  Um_UserSyscode=? ''', um_user_syscode)
    result1 = cursor.fetchall() 
    conn.commit()
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result1]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()
    fig= make_subplots(rows=2, cols=1, vertical_spacing=0.1, subplot_titles=(
        'pie diagram'
    ))
    colors = ['#4CAF50', '#FF9800', '#F44336', '#BDBDBD ']
    trace2 = go.Pie(labels=df['LeadSummary'], values=df['LeadCount'],hole=0.5,textfont_size=8,textfont_color='white',textinfo='label+percent',pull=[0, 0, 0.2, 0],
                  marker=dict(colors=colors,line=dict(color='#f1f1f1', width=1.5)))
    
    # trace2.name = ''
    # trace2.showlegend = False
    fig.add_trace(trace2)
    x=df['LeadCount'].sum()
    fig.update_layout(annotations=[dict(text=str(x),x=0.5, y=0.45, font_size=25, showarrow=False),
               ])
    fig_json=fig.to_json()
    response={'data':fig_json}
    return jsonify(response)

@app.route('/pie2', methods=['GET'])
def main2():
    cmsyscode =str(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    um_user_syscode=str(request.args.get('um_user_syscode'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("EXEC LeadSourceGridOnLeadGraph_PY @CM_syscode= ?,@fromdate= ?,@todate= ?,@um_user_syscode= ?", (cmsyscode,fromdate,todate,um_user_syscode))   
    cursor.execute('''SELECT * FROM rms_live.LeadSourcePY WHERE  um_user_syscode=? ''', um_user_syscode)
    result3 = cursor.fetchall()
    conn.commit()
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result3]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()  
    fig= make_subplots(rows=2, cols=1, vertical_spacing=0.1, subplot_titles=(
        'pie diagram'
    ))
    colors = ['#4CAF50', '#FF9800', '#F44336', '#BDBDBD ']
    trace2 = go.Pie(labels=df['LeadSource'], values=df['LeadCount'],hole=0.5,textfont_size=8,textfont_color='white',textinfo='label+percent',pull=[0, 0, 0.2, 0],
                  marker=dict(colors=colors,line=dict(color='#f1f1f1', width=1.5)))
    
    # trace2.name = ''
    # trace2.showlegend = False
    fig.add_trace(trace2)
    x=df['LeadCount'].sum()
    fig.update_layout(annotations=[dict(text=str(x),x=0.5, y=0.45, font_size=25, showarrow=False),
               ])
    fig_json=fig.to_json()
    response={'data':fig_json}
    return jsonify(response)

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
    response={'data':fig_json}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
