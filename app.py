import os
import requests
from twilio.rest import Client
import flask
import petpy
from petpy import Petfinder
from flask import request, flash

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = flask.Flask(__name__)
app.secret_key = os.getenv("KEY")
# twilio credential
account_sid = os.getenv("SID")
auth_token = os.getenv("TOKEN")
key = os.getenv("OKEY")
secret = os.getenv("OSECRET")
pf = Petfinder(key=key, secret=secret)
client = Client(account_sid, auth_token)

# catAPI
catUrl = "https://api.thecatapi.com/v1/images/search?format=json"
# catFactAPI
cfactUrl = "https://catfact.ninja/fact?max_length=100"
# dogAPI
dogUrl = "https://dog.ceo/api/breeds/image/random"
# dogFactAPI
factUrl = "https://dog-api.kinduff.com/api/facts"
catData = {}
catHeaders = {"Content-Type": "application/json", "x-api-key": os.getenv("KEY")}
cfactData = {}
cfactHeaders = {"Accept": "application/json"}
dogData = {}
dogHeaders = {"Accept": "application/json"}
dfactData = {}
dfactHeaders = {"Accept": "application/json"}


catRes = requests.get(catUrl, headers=catHeaders, data=catData)
cfactRes = requests.get(cfactUrl, headers=cfactHeaders, data=cfactData)
dogRes = requests.get(dogUrl, headers=dogHeaders, data=dogData)
dfactRes = requests.get(factUrl, headers=dfactHeaders, data=dfactData)

catR = catRes.json()
cfactR = cfactRes.json()
dogR = dogRes.json()
dfactR = dfactRes.json()

city = []
state = []
post = []
name = []
link = []
add1 = []
# use twilio to send messages
def orgs(loc):
    org = pf.organizations(
        location=loc,
        results_per_page=10,
        pages=1,
        distance=50,
    )
    for i in org["organizations"]:

        ocity = i["address"]["city"]
        ostate = i["address"]["state"]
        oadd1 = i["address"]["address1"]
        opost = i["address"]["postcode"]
        oname = i["name"]
        olink = i["url"]
        city.append(ocity)
        state.append(ostate)
        add1.append(oadd1)
        post.append(opost)
        name.append(oname)
        link.append(olink)


def replacement(phoneNumber):
    phoneNumber = phoneNumber.replace(" ", "")
    phoneNumber = phoneNumber.replace("-", "")
    phoneNumber = phoneNumber.replace("(", "")
    phoneNumber = phoneNumber.replace(")", "")

    return phoneNumber


def cg():
    cimages = catR[0]["url"]
    cfact = cfactR["fact"]
    dimages = dogR["message"]
    dfact = dfactR["facts"][0]
    return (cimages, cfact, dimages, dfact)


@app.route("/")
def main():
    return flask.render_template("/landingPage.html")


@app.route("/landingPage", methods=["GET", "POST"])
def landingPage():
    return flask.render_template("/landingPage.html")


@app.route("/about", methods=["GET", "POST"])
def about():
    return flask.render_template("/about.html")


@app.route("/cat", methods=["GET", "POST"])
def cat():
    catRes = requests.get(catUrl, headers=catHeaders, data=catData)
    cfactRes = requests.get(cfactUrl, headers=cfactHeaders, data=cfactData)
    catR = catRes.json()
    cfactR = cfactRes.json()
    cimages = catR[0]["url"]
    cfact = cfactR["fact"]
    return flask.render_template("/cat.html", cfact=cfact, cimages=cimages)


@app.route("/getCat", methods=["GET", "POST"])
def getCat():
    if request.method == "POST":
        phoneNumber = request.form.get("phoneNumber")
        replacement(phoneNumber)
        catRes = requests.get(catUrl, headers=catHeaders, data=catData)
        cfactRes = requests.get(cfactUrl, headers=cfactHeaders, data=cfactData)
        catR = catRes.json()
        cfactR = cfactRes.json()
        cimages = catR[0]["url"]
        cfact = cfactR["fact"]
        image = cimages
        message = client.messages.create(
            from_="+13185943649",
            messaging_service_sid=os.getenv("MID"),
            body="\n**CAT fact of the day!**\n" + "\U0001F638 - " + str(cfact),
            media_url=image,
            to="+1" + phoneNumber,
        )
        print(message.sid)
        flash("You have inputted a phone number!")
    return flask.render_template("/cat.html")


@app.route("/dog", methods=["GET", "POST"])
def dog():
    dogRes = requests.get(dogUrl, headers=dogHeaders, data=dogData)
    dfactRes = requests.get(factUrl, headers=dfactHeaders, data=dfactData)
    dogR = dogRes.json()
    dfactR = dfactRes.json()
    dimages = dogR["message"]
    dfact = dfactR["facts"][0]
    return flask.render_template("/dog.html", dfact=dfact, dimages=dimages)


@app.route("/getDog", methods=["GET", "POST"])
def getDog():
    if request.method == "POST":
        phoneNumber = request.form.get("phoneNumber")
        replacement(phoneNumber)
        dogRes = requests.get(dogUrl, headers=dogHeaders, data=dogData)
        dfactRes = requests.get(factUrl, headers=dfactHeaders, data=dfactData)
        dogR = dogRes.json()
        dfactR = dfactRes.json()
        dimages = dogR["message"]
        dfact = dfactR["facts"][0]
        image = dimages
        message = client.messages.create(
            from_="+13185943649",
            messaging_service_sid=os.getenv("MID"),
            body="\n**DOG fact of the day!**\n" + "\n\U0001F436 - " + str(dfact),
            media_url=image,
            to="+1" + phoneNumber,
        )
        print(message.sid)
        flash("You have inputted a phone number!")
    return flask.render_template("/dog.html")


@app.route("/catdog", methods=["GET", "POST"])
def catdog():
    catRes = requests.get(catUrl, headers=catHeaders, data=catData)
    cfactRes = requests.get(cfactUrl, headers=cfactHeaders, data=cfactData)
    dogRes = requests.get(dogUrl, headers=dogHeaders, data=dogData)
    dfactRes = requests.get(factUrl, headers=dfactHeaders, data=dfactData)
    catR = catRes.json()
    cfactR = cfactRes.json()
    dogR = dogRes.json()
    dfactR = dfactRes.json()
    cimages = catR[0]["url"]
    cfact = cfactR["fact"]
    dimages = dogR["message"]
    dfact = dfactR["facts"][0]
    return flask.render_template(
        "/catdog.html", cfact=cfact, cimages=cimages, dfact=dfact, dimages=dimages
    )


@app.route("/getcatdog", methods=["GET", "POST"])
def getcatdog():
    if request.method == "POST":
        phoneNumber = request.form.get("phoneNumber")
        replacement(phoneNumber)
        catRes = requests.get(catUrl, headers=catHeaders, data=catData)
        cfactRes = requests.get(cfactUrl, headers=cfactHeaders, data=cfactData)
        dogRes = requests.get(dogUrl, headers=dogHeaders, data=dogData)
        dfactRes = requests.get(factUrl, headers=dfactHeaders, data=dfactData)
        catR = catRes.json()
        cfactR = cfactRes.json()
        dogR = dogRes.json()
        dfactR = dfactRes.json()
        cimages = catR[0]["url"]
        cfact = cfactR["fact"]
        dimages = dogR["message"]
        dfact = dfactR["facts"][0]
        image = (cimages, dimages)
        message = client.messages.create(
            from_="+13185943649",
            messaging_service_sid=os.getenv("MID"),
            body="\n**CAT and DOG fact of the day!**\n"
            + "\U0001F638 - "
            + str(cfact)
            + "\n\U0001F436 - "
            + str(dfact),
            media_url=image,
            to="+1" + phoneNumber,
        )
        print(message.sid)
        flash("You have inputted a phone number!")
    return flask.render_template("/catdog.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        fback = request.form.get("Suggestion")
        message = client.messages.create(
            from_="+13185943649",
            messaging_service_sid=os.getenv("MID"),
            body="new feedback!\n" + str(fback),
            to="+1" + "8627045775",
        )
        print(message.sid)
        flash("Thank you for the feedback!")
    return flask.render_template("/feedback.html")


@app.route("/adopt", methods=["GET", "POST"])
def adopt():
    if request.method == "POST":
        orgs(request.form.get("State"))
        return flask.render_template(
            "/results.html",
            ocity=city,
            ostate=state,
            oadd1=add1,
            opost=post,
            oname=name,
            olink=link,
            len=len(name),
        )
    return flask.render_template("/adopt.html")


@app.route("/results", methods=["GET", "POST"])
def results():
    return flask.render_template("results.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
