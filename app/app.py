from flask import Flask, request,jsonify, make_response, render_template, send_from_directory, session
from flask_session import Session
from flask_cors import CORS
from flask_sslify import SSLify
import json
import os
import requests
#from bs4 import BeautifulSoup as Soup
from time import sleep, time
import traceback
from modules import database
import json
import logging
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'asd123asd12341asd123'
#CORS(app, supports_credentials=True)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
CORS(app, supports_credentials=True)
# SSLify(app)
# optional if you want to use flask_session
# Session(app)

app.config['UPLOAD_FOLDER'] = "downloads"

logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')




def get_db():
    return next(database.get_db())

@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5050,debug=True)