import os
import secrets
import requests
import random
import json
import flask
from flask import render_template
from dotenv import load_dotenv, find_dotenv

app = flask.Flask(__name__)

caturl = "https://api.thecatapi.com/v1/images/search?format=json"

data = {}
headers = {"Content-Type": "application/json", "x-api-key": os.getenv("KEY")}

res = requests.get(caturl, headers=headers, data=data)

r = res.json()

images = r[0]["url"]


@app.route("/")
def main():
    return flask.render_template("landingPage.html", images=images)


app.run(
    host="localhost",
    port="8081",
    debug=True,
)
