import os
from flask import Flask, render_template, request, redirect, url_for
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
import datetime

from bokeh.charts import Histogram
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import sqlite3

import gensim

app = Flask(__name__)

@app.route('/')
def main():
  return redirect(url_for('predict'))

@app.route('/about')
def about():
  return render_template('about.html')

#Main Process
@app.route('/predict')
def predict():
  Make = request.args.get('Make')
  Model = request.args.get('Model')
  Year = request.args.get('Year')
  Query = str(request.args.get('Query'))

  if Make and Model and Year and Query:
    w2vmodelname = Make + "_" + Model + "_" + Year + "_w2v.model"
    w2vmodel = gensim.models.Word2Vec.load("NLPModels/" + w2vmodelname)
    #target = ['ydm', 'usa', 'index', 'qxp', '2016', '29', 'pm', 'page', 'index', 'securing', 'child', 'restraint', 'seat', 'withchild', 'seat', 'lower', 'anchor', 'system', '32', 'child', 'protector', 'rear', 'door', 'lock', '20', 'clean', 'air', '129', 'climate', 'control', 'air', 'filter', '39', 'filter', 'inspection', '39', 'climate', 'control', 'seat', '136', 'clothes', 'hanger', '139', 'combined', 'instrument', 'see', 'instrument', 'cluster', '54', 'consumer', 'assistance', '12', 'coolant', '32', 'cooling', 'fluid', 'see', 'engine', 'coolant', '32', 'crankcase', 'emission', 'control', 'system', '97', 'cruise', 'control', 'system', '56', 'cruise', 'control', 'switch', '56', 'set', 'cruise', 'control', 'speed', '57', 'increase', 'cruise', 'control', 'set', 'speed', '58', 'decrease', 'cruising', 'speed', '58', 'temporarily', 'accelerate', 'cruise', 'control', '58', 'cancel', 'cruise', 'control', '59', 'resume', 'cruising', 'speed', 'approximately', '20', 'mph', '30', 'km', '59', 'turn', 'cruise', 'control', '60', 'cup', 'holder', '133', 'curtain', 'air', 'bag', '50', '4i', 'dashboard', 'illumination', 'see', 'instrument', 'panel', 'illumination', '55', 'dashboard', 'see', 'instrument', 'cluster', '54', 'day', 'night', 'rearview', 'mirror', '49', 'declaration', 'conformity', '262', 'fcc', '262', 'defogging', 'windshield', '125', 'defroster', 'rear', 'window', '104', 'defrosting', 'windshield', '125', 'dimensions', 'disarmed', 'stage', '15', 'display', 'illumination', 'see', 'instrument', 'panel', 'illumination', '55', 'displays', 'see', 'instrument', 'cluster', '54', 'door', 'locks', '17', 'outside', 'vehicle', '17', 'inside', 'vehicle', '17', 'central', 'door', 'lock', 'switch', '18', 'child', 'protector', 'rear', 'door', 'lock', '20', 'drive', 'mode', 'drive', 'mode', 'integrated', 'control', 'system', '61', 'drive', 'mode', 'integrated', 'control', 'system', '61', 'drive', 'mode', '61', 'eco', 'mode', '61', 'sport', 'mode', '62', 'driver', 'position', 'memory', 'system']
    #testres = w2vmodel.n_similarity( Query.split(' '), target)
    #print(testres)
    '''
    #Parse data if HTTP Status is OK
    if HTTPstatusCode == 200:
      jheader = (jsonRespond.json())['dataset']['column_names']
      jdata = (jsonRespond.json())['dataset']['data']
      stockdata = pd.DataFrame(jdata, columns=jheader)
      stockdata["Date"] = pd.to_datetime(stockdata["Date"])
      print(stockdata.head())
    '''
    #URL feedback
    resurl = "https://s3-us-west-2.amazonaws.com/huaherokupdfs/KIA/Forte/2017/2017_Forte_NaviQG.pdf#page=6"

    #Render Plot
    fig = figure(title = None, plot_width = 800, plot_height = 600, toolbar_location = "below", tools = "crosshair, pan, wheel_zoom, box_zoom, reset")
    data = np.random.uniform(0,1,2000)
    hist, edges = np.histogram(data, density=False, bins=50)
    fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
    fig.xaxis.axis_label = "Similarity"
    fig.yaxis.axis_label = None
    
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig, INLINE)
    html = render_template('predict.html', status = {'code':1, 'msg':'OK'}, predict = {'Make':Make, 'Model':Model, 'Year':Year}, resurl = resurl, plot = {'script':script, 'div':div}, js_resources=js_resources, css_resources=css_resources)
    #else:
    #  html = render_template('predict.html', status = {'code':2, 'msg':'Server Error'}, stock = {'ticker':stockticker, 'period':stockperiod})
  else:
    html = render_template('predict.html', status = {'code':3, 'msg':'Please Enter a valid predict parameters'}, predict = {'Make':'None', 'Model':'None', 'Year':'None'})

  return html

if __name__ == '__main__':
  app.run(debug = True)
