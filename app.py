# python3

import os
import sqlite3

import gensim
import nltk
import pandas as pd
from flask import abort, Flask, jsonify, redirect, render_template, request, url_for
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer, sent_tokenize, word_tokenize

PORT = os.environ.get('PORT', default=8000)
DEBUG = os.environ.get('DEBUG', default=False)

app = Flask(__name__)
try:
    stop_words = set(stopwords.words('english'))
except LookupError as l:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))


def tokenization(text, vocabulary):
    tokenizer = RegexpTokenizer(r'\w+')

    wordsFiltered = []
    words = tokenizer.tokenize(text)
    for w in words:
        wlower = w.lower()
        if wlower not in stop_words and wlower in vocabulary:
            if len(wlower) > 1:  # filter short word
                wordsFiltered.append(wlower)
    return wordsFiltered

def get_car_params(request):
    make = request.args.get('make', default='KIA')
    model = request.args.get('model', default='Rio')
    year = request.args.get('year', default='2017')
    query = str(request.args.get('query'))
    manual_type = str(request.args.get('manual_type', default='OM'))
    return make, model, year, query, manual_type


def get_sql(make, model, year, manual_type):
    con = sqlite3.connect('text/' + make + '.db')
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    sqlcmds = [("SELECT * FROM `" + x[0] + "`;") for x in (cursor.fetchall())
               if model in x[0] and year in x[0] and manual_type in x[0]]
    # need the connection later, so close outside of function
    return sqlcmds, con


def get_data_frame(sqlcmds, con):
    df = pd.DataFrame()
    for sqlcmd in sqlcmds:
        tmpdf = pd.read_sql_query(sqlcmd, con)
        df = df.append(tmpdf)
    # done with connection now
    con.close()
    return df


def get_result(model, query, make='KIA', year='2017', manual_type='OM', num_results=3):
    """
    returns two values (in node style), either True, None which indicates an error happened
    or False, and an array of dictionaries OTF {file:..., page:..., similarity:..., text:...}
    """
    #load from sql to dataframe
    sqlcmds, con = get_sql(make, model, year, manual_type)
    df = get_data_frame(sqlcmds, con)

    #load nlp model
    w2vmodel = gensim.models.Word2Vec.load(
        'models/' + make + '_' + model + '_' + year + '_w2v.model')

    #split query
    querylist = [x.lower() for x in query.split(' ') if x.lower()
                 not in stop_words and x.lower() in w2vmodel.wv.vocab]

    reslist = []
    for idx, row in df.iterrows():
        textlist = tokenization(row['text'], w2vmodel.wv.vocab)
        if len(textlist) > 0:
            try:
                similarity = w2vmodel.n_similarity(querylist, textlist)
            except ZeroDivisionError:
                print('not at all similar')
                similarity = 0
            if similarity > 0:
                entry = {"file": row['filename'], "page": int(row['pagenum']),
                         "text": row['text'], "similarity": similarity, "make": make,
                         "model": model, "year": year}
                reslist.append(entry)

    sorted_reslist = sorted(reslist, key=lambda x: x["similarity"])
    # return top 3
    if len(sorted_reslist) > 0:
        return False, sorted_reslist[-num_results:]
    else:
        return True, None


@app.route('/api')
def predict():
    """
    Example
    /api?make=KIA&model=Rio&year=2017&manual_type=OM&query=bluetooth
    """
    make, model, year, query, manual_type = get_car_params(request)

    if model and query:
        error, top_3 = get_result(
            model, query, make=make, year=year, manual_type=manual_type, num_results=3)
        if error:
            abort(404)
        return jsonify(top_3)
    else:
        abort(404)

@app.route('/voice')
def voice():
    """
    Example
    /voice?make=KIA&model=Rio&year=2017&manual_type=OM&query=bluetooth
    """
    make, model, year, query, manual_type = get_car_params(request)

    if model and query:
        error, top = get_result(
            model, query, make=make, year=year, manual_type=manual_type, num_results=1)
        if error:
            abort(404)
        return jsonify(top_3)
    else:
        abort(404)

@app.route('/')
def home():
    print('home')
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(error):
    return 'No similar passage found', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
