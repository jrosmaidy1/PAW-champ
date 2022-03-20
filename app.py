import os
import requests
from twilio.rest import Client
import flask
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
app = flask.Flask(__name__)

account_sid = os.getenv("SID")
auth_token = os.getenv("TOKEN")
client = Client(account_sid, auth_token)

caturl = "https://api.thecatapi.com/v1/images/search?format=json"

data = {}
headers = {"Content-Type": "application/json", "x-api-key": os.getenv("KEY")}

res = requests.get(caturl, headers=headers, data=data)

r = res.json()

images = r[0]["url"]

message = client.messages.create(
    from_="+13185943649",
    messaging_service_sid=os.getenv("MID"),
    body="You have been catastrophe'd'",
    media_url=images,
    to="+XXXXXXXXXX",
)

print(message.sid)


@app.route("/")
def main():
    return flask.render_template("landingPage.html", images=images)


app.run(
    host="localhost",
    port="8081",
    debug=True,
)
