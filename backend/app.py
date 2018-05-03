# python3

from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import sqlite3
import pandas as pd
import gensim

app = Flask(__name__)
stop_words = set(stopwords.words('english'))
PORT = os.environ.get("PORT", default=8000)
DEBUG = os.environ.get("DEBUG", default=False)

def tokenization(text, vocabulary):
    tokenizer = RegexpTokenizer(r'\w+')

    wordsFiltered = []
    words = tokenizer.tokenize(text)
    for w in words:
        wlower = w.lower()
        if wlower not in stop_words and wlower in vocabulary:
            if len(wlower) > 1: # filter short word
                wordsFiltered.append(wlower)
    return wordsFiltered

def getresult(make, model, year, query, qtype):
    #load from sql to dataframe
    con = sqlite3.connect( "text/" + make + ".db" )
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    sqlcmds = [ ("SELECT * FROM `" + x[0] + "`;") for x in (cursor.fetchall()) if model in x[0] and year in x[0] and qtype in x[0] ]
    df = pd.DataFrame()
    for sqlcmd in sqlcmds:
        tmpdf = pd.read_sql_query(sqlcmd, con)
        df = df.append(tmpdf)

    #load nlp model
    w2vmodel = gensim.models.Word2Vec.load("models/" + make + "_" + model + "_" + year + "_w2v.model")

    #split query
    querylist = [x.lower() for x in query.split(' ') if x.lower() not in stop_words and x.lower() in w2vmodel.wv.vocab]

    reslist = []
    for index, row in df.iterrows():
        textlist = tokenization(row['text'], w2vmodel.wv.vocab)
        if len(textlist) > 0:
            similarity = w2vmodel.n_similarity(querylist, textlist)
            t = (row['filename'], int(row['pagenum']), row['text'], similarity)
            #if reslist[0][3] < similarity:
            reslist.append(t)

    sorted_reslist = sorted(reslist, key=lambda x: x[3])
    # return top 3
    return sorted_reslist[-3:]

# Main Process
@app.route('/api')
def predict():
    '''
    Example
    /api?Make=KIA&Model=Rio&Year=2017&QType=OM&Query=bluetooth
    '''
    Make = request.args.get('Make')
    Model = request.args.get('Model')
    Year = request.args.get('Year')
    Query = str(request.args.get('Query'))
    QType = str(request.args.get('QType'))

    if Make and Model and Year and Query and QType:
        top_3 = getresult(Make, Model, Year, Query, QType)
        resp = top_3[-1]
        return jsonify(top_3)
    else:
        return 'make me a better error message'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)