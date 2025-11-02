from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)


# Variables
new_account = {}



@app.route("/")
def home():
    return render_template("Login.html")

@app.route("/create-account", methods=["GET", "POST"])
def createUser():
    if request.method == "POST":
        user_data = request.get_json()

        firstname   = user_data["firstname"]
        lastname    = user_data["lastname"]
        email       = user_data["email"]
        username    = user_data["username"]
        password    = user_data["password"]
        role        = user_data["role"]
        
        # Stores user data into larger scope variable to move to pandas data frame.
        new_account = user_data

        # STORE NEW USER DATA IN A PANDAS DATA FRAME SEE HOMEWORK 3 FROM 416
        print("Received new account:", new_account)
        return jsonify({"status": "success", "message": f"User {username} created!"})
    
    return render_template("CreateUser.html")

if __name__ == "__main__":
    app.run(port=8080)