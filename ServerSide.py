from flask import Flask, render_template, request, jsonify
import pandas as pd
import csv


# CSV Stuff
FILE_NAME = "User_Accounts.csv"

# Read in data from csv
def csv_read(file) -> list:
    with open(file, 'r') as data:
        csv_reader = csv.DictReader(data)
        results = [row for row in csv_reader]
    return results

# Write data to csv
def csv_write(user_data):
    with open(FILE_NAME, 'a', newline='') as new_file:
        fieldnames = ['firstname', 'lastname', 'email', 'username', 'password', 'role']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(user_data)


# Server Stuff
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("Login.html")

@app.route("/create-account", methods=["GET", "POST"])
def createUser():
    if request.method == "POST":
        user_data = request.get_json()

        # Empty field checks
        if user_data["firstname"] == "":
            return jsonify({"status": "fail", "message": "First name cannot be empty."})
        if user_data["lastname"] == "":
            return jsonify({"status": "fail", "message": "Last name cannot be empty."})
        if user_data["email"] == "":
            return jsonify({"status": "fail", "message": "Email cannot be empty."})
        if user_data["username"] == "":
            return jsonify({"status": "fail", "message": "Username cannot be empty."})
        if user_data["password"] == "":
            return jsonify({"status": "fail", "message": "Password cannot be empty."})
        
        # Existing account checks
        df = pd.read_csv(FILE_NAME)

        # Existing email check
        if user_data["email"] in df["Email"].values:
            return jsonify({"status": "fail", "message": "Account with that email already exists."})
        
        # Existing username check
        if user_data["username"] in df["Username"].values:
            return jsonify({"status": "fail", "message": "Account with that username already exists."})

        # Send user data to csv for storage
        csv_write(user_data)

        print("Received new account:", user_data)
        return jsonify({"status": "success", "message": f"User {user_data["username"]} created!"})
    
    return render_template("CreateUser.html")

if __name__ == "__main__":
    app.run(port=8080)