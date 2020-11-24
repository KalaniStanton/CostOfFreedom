from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go

import json
from pymongo import MongoClient
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import string

def cleanSide(side):
    nopunc = [c for c in side if c not in string.punctuation]
    nopunc = ''.join(nopunc)
    return [word for word in nopunc.split() if word.lower() not in ['government','of','the']]

app = Flask(__name__)

MONGO_HOST = "flask01.network.ncf.edu"
MONGO_DB = "hfmil"
MONGO_USER = "akutlay"
MONGO_PASS = "NCF@2020!"
client = MongoClient('127.0.0.1', 27017)
db = client[MONGO_DB]

cur = db.conflicts.find({},{'_id':0,'location':1,'side_a':1,'side_b':1,'year':1, 'start_date':1, 'ep_end_date':1, 'region':1})
df = pd.DataFrame()
for i in range(cur.count()):
    temp = cur.next()
    df = df.append(temp, ignore_index=True)

df['side_a'] = df['side_a'].apply(cleanSide)
df['side_b'] = df['side_b'].apply(cleanSide)
df['location'] = df['location'].apply(cleanSide)

cur = db.hfi19.find({},{'_id':0,'ISO_code':1,'countries':1,'hf_score':1, 'year':1})
hfDf = pd.DataFrame()
for i in range(cur.count()):
    temp = cur.next()
    hfDf = hfDf.append(temp, ignore_index=True)
hfDf = hfDf.rename({'countries':'country'}, axis = 1)
tempdf = pd.DataFrame()
years = list(hfDf.year.unique())
for year in years:
    codes = hfDf.loc[hfDf['year']==year,'ISO_code']
    for code in codes:
        prop = db.exp_prop.find_one({'Code':code},{'_id':0, str(int(year)):1})
        try:
            prop = list(prop.values())[0]
        except:
            prop = None
        tempdf = tempdf.append({'ISO_code':code, 'year':year,'prop_gdp':prop}, 
                               ignore_index=True)
hfDf = hfDf.merge(tempdf, on = ['ISO_code', 'year'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hfScore')
def hfscorePage():
    return render_template('hf_score.html')

@app.route('/militaryExp')
def militaryexpPage():
    return render_template('military_exp.html')

@app.route('/data-exploration')
def dataexpPage():
    return render_template('data_exp.html')

@app.route('/conflict')
def conflictsPage():
    return render_template('conflict.html')

def hfScoreGraph():
    fig = go.Figure()
    hfDf.sort_values('year', ascending=False, inplace=True)
    years = [year for year in hfDf.year.unique()]

    for year in years:
        fig.add_trace(
            go.Choropleth(
                z = hfDf.loc[hfDf['year']==year,'hf_score'],
                locations = hfDf.loc[hfDf['year']==year,'ISO_code'],
                zmax = 9.12,
                zmin = 3.5))

    fig.data[9].visible = True


    steps = []
    for i in range(len(years)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": "HF scores for the year: " + str(int(years[i]))}],
            label = str(int(years[i]))
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)
        
    sliders = [dict(
        active=10,
        currentvalue={"prefix": "Year: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )


    #fig.show()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def militaryExp():
    fig = go.Figure()
    hfDf.sort_values('year', ascending=False, inplace=True)
    years = [year for year in hfDf.year.unique()]

    for year in years:
        fig.add_trace(
            go.Choropleth(
                z = hfDf.loc[hfDf['year']==year,'prop_gdp'],
                locations = hfDf.loc[hfDf['year']==year,'ISO_code'],
                zmax = 0.1,
                zmin = 0))

    fig.data[9].visible = True


    steps = []
    for i in range(len(years)):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": "Military expenditure as proportion of gdp for the year: " + str(int(years[i]))}],
            label = str(int(years[i]))
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)
        
    sliders = [dict(
        active=10,
        currentvalue={"prefix": "Year: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def createScatterPlot(firstVariable):
    mil_exp = list(db.exp_prop.find({"2017":{'$exists':'true'}, 
                                     'Code':{'$exists':'true'}}, 
                                    {'Code':1, "Country":1, "2017":1, "_id":0}))
    query = list(db.hfi19.find({'year':2017}, 
                               {'ISO_code':1, 'countries':1, str(firstVariable):1, '_id':0}))

    countries = []
    x = []
    y = []
    
    for i in query:
        for j in mil_exp:
            if i['ISO_code'] == j['Code']:
                x.append(j['2017'])
                if(firstVariable in i):
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

def createScatterPlot2(firstVariable,secondVariable):
    cur = db.hfi19.find({},{'_id':0,'ISO_code':1,'countries':1,str(firstVariable):1,str(secondVariable):1, 'year':1})
    hfDf = pd.DataFrame()
    for i in range(cur.count()):
        temp = cur.next()
        hfDf = hfDf.append(temp, ignore_index=True)


    fig = px.scatter(hfDf, x=str(firstVariable), y=str(secondVariable), animation_frame="year", color="countries")
    #fig.show()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON



@app.route('/data/militaryExp', methods=['GET', 'POST'])
def milexp():
    graphJSON= militaryExp()
    return graphJSON

@app.route('/data/conflictInfo', methods=['GET', 'POST'])
def conflict():
    graphJSON= conflictInfo()
    return graphJSON

@app.route('/data/hfScore', methods=['GET', 'POST'])
def hfscore():
    graphJSON = hfScoreGraph()
    return graphJSON


@app.route('/data/scatter_only', methods=['GET', 'POST'])
def scatter():

    firstVariable = request.args['firstVariable']
    graphJSON= createScatterPlot(firstVariable)

    return graphJSON

@app.route('/data/scatter', methods=['GET', 'POST'])
def scatter2():

    firstVariable = request.args['firstVariable']
    secondVariable = request.args['secondVariable']
    graphJSON= createScatterPlot2(firstVariable,secondVariable)

    return graphJSON

if __name__ == '__main__':
    app.run(debug=True)