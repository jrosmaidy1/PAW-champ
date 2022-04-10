import os
import requests
import flask
import json
import petpy
from petpy import Petfinder
from dotenv import load_dotenv, find_dotenv
from flask import request, flash

load_dotenv(find_dotenv())

app = flask.Flask(__name__)


# @app.route("/org")
# def org():
#     return flask.render_template()


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        key = os.getenv("OKEY")
        secret = os.getenv("OSECRET")
        pf = Petfinder(key=key, secret=secret)
        org = pf.organizations(
            location=request.form.get("State"),
            results_per_page=10,
            pages=1,
            distance=50,
        )
        city = []
        state = []
        post = []
        name = []
        link = []
        add1 = []
        for i in org["organizations"]:

            ocity = i["address"]["city"]
            ostate = i["address"]["state"]
            oadd1 = i["address"]["address1"]
            oadd2 = i["address"]["address2"]
            opost = i["address"]["postcode"]
            oname = i["name"]
            olink = i["url"]
            city.append(ocity)
            state.append(ostate)
            add1.append(oadd1)
            post.append(opost)
            name.append(oname)
            link.append(olink)
            print(org)
        return flask.render_template(
            "org.html",
            ocity=city,
            ostate=state,
            oadd1=add1,
            opost=post,
            oname=name,
            olink=link,
            len=len(name),
        )
    return flask.render_template("index.html")


@app.route("/dog", methods=["GET", "POST"])
def dog():
    if request.method == "POST":
        dogUrl = "https://dog.ceo/api/breeds/image/random"
        factUrl = "https://dog-api.kinduff.com/api/facts"
        factData = {}
        factHeaders = {"Accept": "application/json"}
        dogData = {}
        dogHeaders = {"Accept": "application/json"}
        factRes = requests.get(factUrl, headers=factHeaders, data=factData)
        factR = factRes.json()
        fact = factR["facts"]
        dogRes = requests.get(dogUrl, headers=dogHeaders, data=dogData)
        dogR = dogRes.json()
        dog = dogR["message"]
        return flask.render_template("dog.html", fact=fact, dog=dog)


app.run(host="127.0.0.1", port=5000, debug=True)
