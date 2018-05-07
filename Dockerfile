FROM python:3

COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
# Need to download the NLTK data
# We may already have it, but this fixes it so whatever
EXPOSE 8000

CMD ["python", "app.py"]
