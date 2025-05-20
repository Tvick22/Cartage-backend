from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from model.leaderboard import LeaderboardEntry
from __init__ import app, db
from model.item import Item  # Assuming you have an Item model defined in the `model` folder
from flask import Flask, render_template

app = Flask(__name__)

# Initialize Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["https://TVick22.github.io"])

# ------------------------------
# USER DATA API
# ------------------------------
#static database of user information used to understand API not important for website 
@app.route('/api/data')
def get_data():
    InfoDb = [
        {"FirstName": "Nolan", "LastName": "Yu", "DOB": "October 7", "Residence": "San Diego", "Email": "nolanyu2@gmail.com", "Owns_Cars": ["Mazda"]},
    ]
    return jsonify(InfoDb)


