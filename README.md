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
```

## Backend (API)

```sh
cd backend
/usr/bin/python3 app.py
```

will start a Flask server on port 8000 (configurable with a PORT environment variable). The debug param is also configurable, eg, `DEBUG=True PORT=8080 python3 app.py` will start the server in debug mode on port 8080.
