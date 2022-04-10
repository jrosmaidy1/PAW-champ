import email
import os
from datetime import datetime

import flask
import petpy
import requests
from dotenv import find_dotenv, load_dotenv
from flask import flash, redirect, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from petpy import Petfinder
from twilio.rest import Client
from wtforms import (BooleanField, DecimalField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)

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

        add1.clear()
        return flask.render_template("/adopt.html")
    return redirect(url_for("landingPage"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
