from flask import Flask
import pyodbc
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import plotly.offline as py
from plotly.tools import make_subplots
import plotly.express as px




server = 'ttplsqleu.database.windows.net'
database = 'rms_live'
username = 'ttplsqladmineu'
password = 'TTPL@123'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

app = Flask(__name__)

# connecting to server 

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


# giving names to plots

    fig = make_subplots(rows=5, cols=1, vertical_spacing=0.1, subplot_titles=(
        'Leads From Sources',
        'Leads Status',
        'Leads Counts and Status',
        'Count Leads from sources',
        'Leads Count Table'
    ))
    
    # inbuild trace name assigned (like trace 0 ,trace 1 ,....)
    
    # fig.add_trace(
    #     go.Histogram(x=df['COL_ContactLabel']),
    #     row=1, col=1,
    #     # name='Leads From Sources'
    # )

    #Giving name to the trace 

    T0 = go.Histogram(x=df['COL_ContactLabel'])
    T0.name = 'Leads From Sources'
    fig.add_trace(T0, row=1, col=1)

    # fig.add_trace(
    #     go.Histogram(x=df['ls_description']),
    #     row=2, col=1,
    #     # name='Leads Status'
    # )

    T1 = go.Histogram(x=df['ls_description'])
    T1.name = 'Leads Status'
    fig.add_trace(T1, row=2, col=1)

    colors = {
        'WIP': 'blue',
        'Closed': 'green',
        'Lost Lead': 'red',
        'Junk Lead':'yellow',
        'Closed-Won':'gray',
        'User Link':'white',
        'Reseller':'black',
        'Quotation':'pink',
        'Contact in Future':'green'
    }

    # fig.add_trace(
    #     go.Bar(x=df['COL_ContactLabel'], y=df['ls_description'], marker=dict(color=[colors.get(category,'blue') for category in df['ls_description']])),
    #     row=3, col=1,
    #     # name='Leads Counts and Status'
    # )
    T2 = go.Bar(x=df['COL_ContactLabel'], y=df['ls_description'], marker=dict(color=[colors.get(category,'blue') for category in df['ls_description']]))
    T2.name = 'Leads Counts and Status'
    fig.add_trace(T2, row=3, col=1)
    
    # fig.add_trace(
    #     go.Histogram(y=df['COL_ContactLabel'], histfunc='count'),
    #     row=4, col=1,
    #     # name='Count Leads from sources'
    # )
     
    T3 = go.Histogram(y=df['COL_ContactLabel'], histfunc='count')
    T3.name = 'Count Leads from sources'
    fig.add_trace(T3, row=4, col=1)


    # fig.add_trace(
    #     go.Bar(x=df.index, y=df['ls_description'], marker=dict(color=[colors.get(category,'blue') for category in df['ls_description']])),
    #     row=5, col=1,
    #     name='Leads Count Table'
    # )

    T4 = go.Bar(x=df.index, y=df['ls_description'], marker=dict(color=[colors.get(category, 'blue') for category in df['ls_description']]))
    T4.name = 'Leads Count Table'
    fig.add_trace(T4, row=5, col=1)


 #Pie diagram
  
#     count_df = df['ls_description'].value_counts().reset_index()
#     count_df.columns = ['ls_description', 'count']
#     df_merged = df.merge(count_df, on='ls_description')

#     fig.add_trace(
#     go.Pie(labels=df_merged['ls_description'], values=df_merged['count']),
#     row=5, col=1
# )

    fig.update_layout(
        height=5000, 
        width=1200   
    )


    leads_count = df.groupby(['COL_ContactLabel', 'ls_description']).size().reset_index(name='Count')
    total_leads_count = leads_count.groupby('COL_ContactLabel')['Count'].sum().reset_index(name='Total')
    leads_count = leads_count.merge(total_leads_count, on='COL_ContactLabel')
    leads_count['Percentage'] = (leads_count['Count'] / leads_count['Total']) * 100

    def format_color_groups(values):
        if values <= 30:
            return 'color:red; border-collapse:collapse; border:1px solid black;'
        elif values <= 50:
            return 'color:green; border-collapse:collapse; border:1px solid black;'
        else:
            return 'color:blue; border-collapse:collapse; border:1px solid black;'

    leads_count_styled = leads_count.style.applymap(format_color_groups)
    leads_count_styled = leads_count_styled.set_table_attributes('style="border-collapse:collapse; border:1px solid black;"')

    table_trace = go.Table(header=dict(values=list(leads_count_styled.columns)),
                           cells=dict(values=leads_count.values.T))

    table_fig = go.Figure(data=[table_trace])
    table_fig.update_layout(height=1200, width=1000)

    fig_html = py.plot(fig, output_type='div', include_plotlyjs='cdn')
    table_html = table_fig.to_html(full_html=False)

    return fig_html + table_html

if __name__ == '__main__':
    app.run(debug=True)

