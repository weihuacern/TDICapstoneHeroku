# TDICapstoneHeroku

Quick remote build and test:
```sh
heroku create --buildpack https://github.com/kennethreitz/conda-buildpack.git
git push heroku master
heroku ps:scale web=1
heroku open
```

Local test:
```sh
heroku local web
# or
python3 app.py
```

## API / Frontend

Running `python3 app.py` starts up a server that has the route `/api`, which returns JSON. It will also serve static files from `/`, `/static`, and `/templates`. The frontend logic is in `static/js/main.js` - it's pretty straightforward. 

The server is a Flask server on port 8000 (configurable with a PORT environment variable). The debug param is also configurable, eg, `DEBUG=True PORT=5050 python3 app.py` will start the server in debug mode on port 5050.

### Todo

* Use [PDFjs](https://mozilla.github.io/pdf.js/examples/) so we can eagerly fetch the PDFs, and just render them when the user presses the button - it will seem much faster. We will start to fetch on any dropdown change, but throttled so we don't go too crazy
* NEXT button to jump to next most similar result - this will also benefit from PDFjs, since we don't need to reload the whole doc, we can just move pages
* Once we are comfortable deleting the OLD app, then we can also delete the directories `/NLPModels` and `/TextDBs`
* Make sure _all_ required packages are in a file such as requirements.txt
* Clean up the database situation - ideally should connect to MySQL instance with all MMY combos
* Deploy on AWS - this will involve putting the app behind gunicorn... may as well Dockerize it...
* make a `/voice` endpoint, that returns something like "On page x of the `manual_type` manual, it says ... " 
* Improve embedding - this would mean (possibly) leaving `gensim`, which sucks as it has a nice API. So it's only worth it for a big improvement
