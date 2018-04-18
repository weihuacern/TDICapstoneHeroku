# TDICapstoneHeroku

Quick remote build and test:
```
heroku create --buildpack https://github.com/kennethreitz/conda-buildpack.git
git push heroku master
heroku ps:scale web=1
heroku open
```

Local test:
```
heroku local web
```
