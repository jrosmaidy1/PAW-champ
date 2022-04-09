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
            results_per_page=15,
            pages=1,
            distance=50,
        )
        city = []
        state = []
        post = []
        name = []
        link = []
        for i in org["organizations"]:

            ocity = i["address"]["city"]
            ostate = i["address"]["state"]
            opost = i["address"]["postcode"]
            oname = i["name"]
            olink = i["url"]
            city.append(ocity)
            state.append(ostate)
            post.append(opost)
            name.append(oname)
            link.append(olink)
        return flask.render_template(
            "org.html",
            ocity=city,
            ostate=state,
            opost=post,
            oname=name,
            olink=link,
            len=len(name),
        )
    return flask.render_template("index.html")


app.run(host="127.0.0.1", port=5000, debug=True)
