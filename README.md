# Cat-astrophe!

**Deployment:** Check it out [here](http://www.cat-astrophe.tech/)!

## Introduction
### Sign up with your phone number to receive random cat fact and an image from a bot.
<p align="center">
<img src = "https://user-images.githubusercontent.com/74800828/159157591-dc9731d6-b340-4b1e-b5d5-94fbf7b86bad.png">
<img src = "https://user-images.githubusercontent.com/74800828/159168274-ca6f64f4-3030-421f-a192-151624dd94cc.jpg">
</p>

## Setup Instructions
To run the project clone it into local directory create a ```.env``` file containing below mentioned parameters

- KEY = Get key by signing up with [CatAPI](https://thecatapi.com/signup)
- SID = Get SID by signing up with [Twilio](https://console.twilio.com/)
- TOKEN =  Get TOKEN by signing up with [Twilio](https://console.twilio.com/)
- MID = Get MID by signing up with [Twilio](https://console.twilio.com/)

Install all the requirements from ```requirements.txt```
```bash
Flask==2.0.2
Jinja2==3.0.2
requests==2.22.0
twilio==7.7.1
gunicorn==19.3.0
python-dotenv==0.19.1
```
## To run the app
You can start the project by executing ```python app.py``` or ```python3 app.py``` command.
