from flask import Flask, jsonify,request
from plotly.tools import make_subplots
import pyodbc
import pandas as pd
import plotly.graph_objects as go
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
    um_user_syscode=str(request.args.get('um_user_syscode'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor() 
    cursor.execute("EXEC PyGraphData_status @cmsyscode= ?,@fromdate= ?,@todate= ?,@um_user_syscode=?", (cmsyscode,fromdate,todate,um_user_syscode))   
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    NEXT = cursor.nextset()
    result2 = cursor.fetchall()
    columns2 = [column[0] for column in cursor.description]
    result_reshaped2 = [tuple(row) for row in result2]
    df2= pd.DataFrame(result_reshaped2, columns=columns2)
    cursor.close()
    conn.close()

    fig = make_subplots(rows=1, cols=2, vertical_spacing=0.15, subplot_titles=('<b>Lead Status<b>','<b>Lead Source<b>', ))
    T1 = go.Histogram(x=df['ls_description'],marker_color='#0bb4c6')
    T1.name = ''                                         
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(height=400, width=1330 ,margin=dict(l=50, r=50, t=100, b=100))
    T2 = go.Histogram(x=df2['COL_ContactLabel'],marker_color='#8BC34A')
    T2.name=''
    fig.add_trace(T2,row=1,col=2)
    xaxis_labels =df2['COL_ContactLabel'].unique()
    updated_labels = []
    for label in xaxis_labels:
        if ' ' in label:
            label_parts = label.split(' ')
            updated_labels.append('<br>'.join(label_parts))
        else:
            updated_labels.append(label)        
    fig.update_layout(height=400, width=1350,margin=dict(l=50, r=50, t=50, b=50),plot_bgcolor='white',bargap=0.2, showlegend=False,
            xaxis2=dict(
            tickmode='array',
            tickvals=list(range(0, len(updated_labels)+1)),
            ticktext=updated_labels,
            showticklabels=True,
            tickfont=dict(size=12),
            automargin=True,))   
    fig.update_annotations(font_size=16)
    fig.update_layout(
    modebar={'remove': ['zoom2d', 'autoscale2d', 'pan2d', 'lasso2d', 'resetScale2d','logo','ModeBar'],
              },showlegend=False,)   
    fig_dict = fig.to_dict()
    fig_dict['data'][0]['x'] = fig_dict['data'][0]['x'].tolist()
    fig_dict['data'][1]['x'] = fig_dict['data'][1]['x'].tolist()
    response = {'data': fig_dict}
    return jsonify(response)


@app.route('/line', methods=['GET'])
def main3():
    cmsyscode =str(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    um_user_syscode=str(request.args.get('um_user_syscode'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor() 
    cursor.execute("EXEC PyGraphData_status  @cmsyscode= ?,@fromdate= ?,@todate= ?,@um_user_syscode=?", (cmsyscode,fromdate,todate,um_user_syscode))   
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    NEXT = cursor.nextset()
    result2 = cursor.fetchall()
    columns2 = [column[0] for column in cursor.description]
    result_reshaped2 = [tuple(row) for row in result2]
    df2= pd.DataFrame(result_reshaped2, columns=columns2)
    cursor.close()
    conn.close()

    result=df.merge(df2, left_on='LM_Syscode', right_on='LM_Syscode')[['COL_ContactLabel', 'ls_description']]
    color_map = {
   'Lost Lead': 'rgb(255, 0, 0)',    
    'Closed': '#4CAF50',    
    'WIP': '#FF9800', 
    'Junk Lead' :'gray',
    'Contact in Future':' #BA68C8',
    'Other':'gray',
    }
    df['color'] = df['ls_description'].map(color_map)
    counts =result.groupby(['COL_ContactLabel', 'ls_description']).size().reset_index(name='count')
    fig = px.bar(counts, x='COL_ContactLabel', y='count', color='ls_description', 
             title=' % Of  Leads Conversions From Sources', barmode='group', text_auto='ls_description')
    for ls_description, color in color_map.items():
        fig.for_each_trace(lambda t: t.update(marker_color=color) if t.name == ls_description else ())
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False,  hovertemplate='%{x}<br><b>%{y}</b>') # hovertemplate are used to adjust which data has to be shown when we hover mouse cursor
    fig.update_layout(xaxis=dict(title='<b>Sources<b>'),yaxis=dict(title='<b>Count<b>'),legend=dict(title='<b>Lead Status<b>'),
                title=dict(text="<b>Lead Conversions From Sources<b>"),
                plot_bgcolor='white',
                 height=600, width=1350,
                 font_size=14)    
    fig.update_layout(
    modebar={'remove': ['zoom2d', 'autoscale2d', 'pan2d', 'lasso2d', 'resetScale2d','logo','ModeBar']},
    showlegend=True,)
    fig_json = fig.to_json()
    return fig_json

if __name__ == '__main__':
    app.run(debug=True)










