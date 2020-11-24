import pandas as pd
import plotly.express as px
from plotly.offline import plot
from pymongo import MongoClient

client = MongoClient()
db = client.hfmil

def createScatterPlot(firstVariable):
    '''
    Parameters
    ----------
    firstVariable : TYPE
        DESCRIPTION.

    Returns
    -------
    graphJSON : TYPE
        DESCRIPTION.

    Takes in a selection from dropdown menu, queries the HFI data, 
    Queries the Military Expenditure/GDP, 
    Appends to pandas DataFrame,
    Creates interactive Plotly scatterplot
    '''
    mil_exp = list(db.exp_prop.find({"2017":{'$exists':'true'}, 
                                     'Code':{'$exists':'true'}}, 
                                    {'Code':1, "Country":1, "2017":1, "_id":0}))
    query = list(db.hfi19.find({'year':2017}, 
                               {'ISO_code':1, 'countries':1, 'pf_ss_women':1, '_id':0}))

    countries = []
    x = []
    y = []
    
    for i in query:
        for j in mil_exp:
            if i['ISO_code'] == j['Code']:
                x.append(j['2017'])
                y.append(i[firstVariable])
                countries.append(i['countries'])
            
    df = pd.DataFrame(list(zip(countries, x, y)),
                      columns = ['Country', 'Military Expenditure/GDP', firstVariable])

    fig = px.scatter(df, x='Military Expenditure/GDP', y=firstVariable, color='Country')
    fig.update_traces(marker=dict(size=10,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
    # plot(fig)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON