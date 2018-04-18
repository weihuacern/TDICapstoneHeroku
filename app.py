import os
from flask import Flask, render_template, request, redirect, url_for
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
import datetime

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
stopWords = set(stopwords.words('english'))

@app.route('/')
def main():
  return redirect(url_for('predict'))

@app.route('/about')
def about():
  return render_template('about.html')


def tokenization(text, vocabulary):
  tokenizer = RegexpTokenizer(r'\w+')
  #stopWords = set(stopwords.words('english'))
    
  wordsFiltered = []
  words = tokenizer.tokenize(text)
  for w in words:
    wlower = w.lower()
    if wlower not in stopWords and wlower in vocabulary:
      if len(wlower) > 1: # filter short word
        wordsFiltered.append(wlower)
  return wordsFiltered

def getresult(make, model, year, query, qtype):
  #load from sql to dataframe
  con = sqlite3.connect( "TextDBs/" + make + "TextInfo.db" )
  cursor = con.cursor()
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  sqlcmds = [ ("SELECT * FROM `" + x[0] + "`;") for x in (cursor.fetchall()) if model in x[0] and year in x[0] and qtype in x[0] ]
  df = pd.DataFrame()
  for sqlcmd in sqlcmds:
    tmpdf = pd.read_sql_query(sqlcmd, con)
    df = df.append(tmpdf)

  #load nlp model
  w2vmodel = gensim.models.Word2Vec.load("NLPModels/" + make + "_" + model + "_" + year + "_w2v.model")
  
  #split query
  querylist = [x.lower() for x in query.split(' ') if x.lower() not in stopWords and x.lower() in w2vmodel.wv.vocab]

  reslist = []
  for index, row in df.iterrows():
    textlist = tokenization(row['text'], w2vmodel.wv.vocab)
    if len(textlist) > 0:
      similarity = w2vmodel.n_similarity( querylist, textlist)
      thistuple = (row['filename'], int(row['pagenum']), similarity)
      reslist.append(thistuple)

  sorted_reslist = sorted(reslist, key=lambda x: x[2])
  #print(sorted_reslist)
  return sorted_reslist
  #return [("2017_Forte_FFG.pdf", 16, 0.124), 
  #        ("qpdfHacked_2017_Forte_OM.pdf", 25, 0.924)]

#Main Process
@app.route('/predict')
def predict():
  Make = request.args.get('Make')
  Model = request.args.get('Model')
  Year = request.args.get('Year')
  Query = str(request.args.get('Query'))
  QType = str(request.args.get('QType'))

  if Make and Model and Year and Query and QType:
    '''
    #Parse data if HTTP Status is OK
    if HTTPstatusCode == 200:
      print(stockdata.head())
    '''
    predres = getresult(Make, Model, Year, Query, QType)
    #URL feedback
    resurl = "https://s3-us-west-2.amazonaws.com/huaherokupdfs/" + Make + "/" + Model + "/" + Year + "/" + predres[-1][0] + "#page=" + str(predres[-1][1])

    #Render Plot
    fig = figure(title = None, plot_width = 800, plot_height = 600, toolbar_location = "below", tools = "crosshair, pan, wheel_zoom, box_zoom, reset")
    #data = np.random.uniform(0,1,2000)
    data = np.array( [x[2] for x in predres] )
    hist, edges = np.histogram(data, density=False, bins=50)
    fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")
    fig.xaxis.axis_label = "Similarity"
    fig.yaxis.axis_label = "Number of Entries"
    
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
