import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, plot, iplot

client = MongoClient()
db = client.hfmil

def drop_down_plots(query):
	country_list = []
    iso_code_list = []
    hfi_score_list = []
    result = list(db.hfi19.find({'year':2017}, {'ISO_code':1, 'countries':1, str(query):1, '_id':0})) 
    for i in result:
        try:
			hfi_score_list.append(i[query])
			country_list.append(i['countries'])
			iso_code_list.append(i['ISO_code'])
		except:
			continue
	df = pd.DataFrame(list(zip(country_list, iso_code_list, hfi_score_list)), columns =['Country', 'ISO', query])
	return df

    data = dict(type = 'choropleth',
           locations = df['ISO'],
           z = df[query],
           text = df['Country'],
           colorbar = {'title':title})

    layout = dict(geo = dict(showframe = False,
             projection = {'type':"equirectangular"}))

    choromap3 = go.Figure(data=[data],layout = layout)

    iplot(choromap3)