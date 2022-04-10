import email
import os
from datetime import datetime

import flask
import petpy
import requests
from dotenv import find_dotenv, load_dotenv
from flask import flash, redirect, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from petpy import Petfinder
from twilio.rest import Client
from wtforms import BooleanField, DecimalField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

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

# database flask config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# initialize database
db = SQLAlchemy(app)

# login manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# loads user
@login_manager.user_loader
def load_user(name):
    """Get the current user name"""
    return Users.query.get(name)


# Users database model
class Users(db.Model, UserMixin):
    # nullable cannot be empty, unique email cannot be repeated
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string
    def __repr__(self):
        return "<Name %r>" % self.name


# Free database model?


# Premium database model?


# Adoption database model #### WIP ####
# class Adopt(db.model):
#     id = db.Column(db.Integer, primary_key=True)


# flask RegistrationForm
class RegistrationForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

    # validates user's email, returns error if email is taken
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


# flask LoginForm class
class LoginForm(FlaskForm):

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Login")


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

# returns cat and dog facts in json format
catR = catRes.json()
cfactR = cfactRes.json()
dogR = dogRes.json()
dfactR = dfactRes.json()

# initializes result objects
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


# fixes phone number for form input
def replacement(phoneNumber):
    phoneNumber = phoneNumber.replace(" ", "")
    phoneNumber = phoneNumber.replace("-", "")
    phoneNumber = phoneNumber.replace("(", "")
    phoneNumber = phoneNumber.replace(")", "")

    return phoneNumber


# parses json files for cat and dog images and facts
def cg():
    cimages = catR[0]["url"]
    cfact = cfactR["fact"]
    dimages = dogR["message"]
    dfact = dfactR["facts"][0]
    return (cimages, cfact, dimages, dfact)


@app.route("/")
def main():
    """
    Main page, requires user authentication to see content
    """
    return flask.render_template("/landingPage.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    """
    Registration page, requires name and email
    """
    form = RegistrationForm()
    name = None  # initialize name
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash("User added successfully, log in using your email")
            return redirect(url_for("login"))

        name = form.name.data

        # clear form
        form.name.data = ""
        form.email.data = ""
    return flask.render_template(
        "/registration.html", form=form, name=name, email=email
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page, requires email
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful, please check email")
    return flask.render_template("/login.html", form=form, email=email)


@app.route("/logout")
def logout():
    """
    Log user out and redirect to login page
    """

    logout_user()
    return redirect(url_for("login"))


@app.route("/landingPage", methods=["GET", "POST"])
def landingPage():
    """
    Landing page detailing what our website offers
    """
    return flask.render_template("/landingPage.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    """
    Home page to view adoptions
    """
    if current_user.is_authenticated:
        name = current_user.name
        email = current_user.email
        return flask.render_template("/home.html", name=name, email=email)

    return redirect(url_for("landingPage"))


@app.route("/about", methods=["GET", "POST"])
def about():
    """
    Showcases development team's bio
    """
    return flask.render_template("/about.html")


@app.route("/cat", methods=["GET", "POST"])
def cat():
    """
    Uses Cat and Cat Fact API to retrieve image and fact
    """
    cimages = catR[0]["url"]
    cfact = cfactR["fact"]
    return flask.render_template("/cat.html", cfact=cfact, cimages=cimages)


@app.route("/getCat", methods=["GET", "POST"])
def getCat():
    """
    Twilio API to receive a text with cat fact and cat image
    """
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
    """
    Uses Dog and Dog Fact API to retrieve image and fact
    """
    dimages = dogR["message"]
    dfact = dfactR["facts"][0]
    return flask.render_template("/dog.html", dfact=dfact, dimages=dimages)


@app.route("/getDog", methods=["GET", "POST"])
def getDog():
    """
    Twilio API to receive a text with cat fact and cat image
    """
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
    """
    Retrieves both cat and dog facts and images
    """
    cimages = catR[0]["url"]
    cfact = cfactR["fact"]
    dimages = dogR["message"]
    dfact = dfactR["facts"][0]
    return flask.render_template(
        "/catdog.html", cfact=cfact, cimages=cimages, dfact=dfact, dimages=dimages
    )


@app.route("/getcatdog", methods=["GET", "POST"])
def getcatdog():
    """
    Sends both cat and dog facts and images as a text message
    """
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
    """
    Feedback page to send page feedback to development team
    """
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
    """
    Retrieves results from PetFinder API to find local shelters
    """
    if current_user.is_authenticated:
        try:
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
        except:
            ValueError
            flash("You have entered an invalid location")
            return redirect(url_for("adopt"))
    return redirect(url_for("landingPage"))


@app.route("/results", methods=["GET", "POST"])
def results():
    """
    Results page displays a list of local shelters
    """
    if current_user.is_authenticated:
        return flask.render_template("results.html")
    return redirect(url_for("landingPage"))


@app.route("/searchAgain", methods=["GET", "POST"])
def searchAgain():
    """
    Search a new location for local shelters
    """
    if current_user.is_authenticated:
        city.clear()
        state.clear()
        post.clear()
        name.clear()
        link.clear()
        add1.clear()
        return flask.render_template("/adopt.html")
    return redirect(url_for("landingPage"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
