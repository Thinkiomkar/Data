from flask import Flask, jsonify,request
import pyodbc
import pandas as pd
import plotly.offline as py
import plotly.graph_objects as go
from plotly.tools import make_subplots
import config

server = config.SQL_SERVER
database = config.SQL_DATABASE
username = config.SQL_USERNAME
password = config.SQL_PASSWORD
connection_string = config.SQL_CONNECTION_STRING

app = Flask(__name__)
@app.route('/', methods=['GET'])
def main():
    cmsyscode =int(request.args.get('cmsyscode'))
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


    fig = make_subplots(rows=1, cols=2, vertical_spacing=0.1, subplot_titles=(
        'pie diagram','Lead Status',
    ))
    T1 = go.Histogram(x=df['ls_description'],marker_color='#0bb4c6')
    T1.name = ''                                           # remove trace name display
    T1.showlegend=False                                   #to remove trace colour box
    fig.add_trace(T1, row=1, col=1)
    fig.update_layout(
        height=400, 
        width=1330 ,
         margin=dict(l=50, r=50, t=100, b=100) 
    )
    T2 = go.Histogram(x=df['COL_ContactLabel'],marker_color='#8BC34A')
    T2.name=''
    T2.showlegend=False
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
        height=400, width=1350,
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

@app.route('/home', methods=['GET'])
def main1():
    cmsyscode =int(request.args.get('cmsyscode'))
    fromdate=str(request.args.get('fromdate'))
    todate=str(request.args.get('todate'))
    um_user_syscode=int(request.args.get('um_user_syscode'))
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("EXEC LeadSourceGridOnLeadGraph  @CM_syscode= ?,@fromdate= ?,@todate= ?,@um_user_syscode= ?", (cmsyscode,fromdate,todate,um_user_syscode))  
    result = cursor.fetchall() 
    columns = [column[0] for column in cursor.description]
    result_reshaped = [tuple(row) for row in result]
    df= pd.DataFrame(result_reshaped, columns=columns)
    cursor.close()
    conn.close()

    fig= make_subplots(rows=1, cols=2, vertical_spacing=0.1, subplot_titles=(
        'pie diagram'
    ))
    top_sources = df['COL_ContactLabel'].value_counts().nlargest(4)
    trace2 = go.Pie(labels=top_sources.index, values=top_sources)
    trace2.name = ''
    trace2.showlegend = False
    fig.add_trace(trace2)
    
    fig_dict = fig.to_dict()
    fig_dict['data'][0]['x'] = fig_dict['data'][0]['x'].tolist()

    response = {'data': fig_dict}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
