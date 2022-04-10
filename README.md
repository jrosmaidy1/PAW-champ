# PAW-Champ!

## Introduction
### Sign up with your name and email to find local shelters and receive random cat/dog facts and images.
<p align="center">
<img src = "https://user-images.githubusercontent.com/74800828/159157591-dc9731d6-b340-4b1e-b5d5-94fbf7b86bad.png">
<img src = "https://user-images.githubusercontent.com/89946346/162639286-19e4bf62-3bb5-42a4-9e7b-2a689aa66a2e.png">
</p>

## Setup Instructions
To run the project clone it into local directory create a ```.env``` file containing below mentioned parameters

- KEY = Get KEY by signing up with [CatAPI](https://thecatapi.com/signup)
- SID = Get SID by signing up with [Twilio](https://console.twilio.com/)
- TOKEN =  Get TOKEN by signing up with [Twilio](https://console.twilio.com/)
- MID = Get MID by signing up with [Twilio](https://console.twilio.com/)
- OKEY = Get OKEY by signing up with [PetFinder](https://www.petfinder.com/developers/)
- OSECRET = Get OSECRET by signing up with [PetFinder](https://www.petfinder.com/developers/)
- PHONE = Protect your PHONE number when using Twilio's API by using it as an .env variable


Install all the requirements 

```pip install -r requirements.txt``` or  ```pip3 install -r requirements.txt```
```bash
Flask==2.0.2
Jinja2==3.0.2
requests==2.22.0
twilio==7.7.1
gunicorn==19.3.0
python-dotenv==0.19.1
Flask-Login==0.6.0
Flask-SQLAlchemy==2.5.1
Flask-WTF==1.0.1
Jinja2==3.0.2
petpy==2.3.1
```

## To run the app
You can start the project by executing ```python app.py``` or ```python3 app.py``` command.
