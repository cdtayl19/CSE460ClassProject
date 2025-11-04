from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
import csv

CURRENT_USER = None

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

def csv_write_new_club_requests(club_request_data):
    with open("NewClubRequests.csv", 'a', newline='') as new_file:
        fieldnames = ['submittedBy', 'clubName', 'topic', 'description']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(club_request_data)


# Server Stuff
app = Flask(__name__)
app.secret_key = "32895"


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/current-user", methods=["GET", "POST"])
def get_current_user():
    if request.method == "GET":
        if "current_user" in session:
            return jsonify({"status": "success", "user": session["current_user"]})
        else:
            return jsonify({"status": "fail", "message": "No user logged in."})


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_data = request.get_json()

        # Empty field check  -- consider moving to client side
        if user_data["username"] == "":
            return jsonify({"status": "fail", "message": "Must enter valid username."})
        if user_data["password"] == "":
            return jsonify({"status": "fail", "message": "Must enter valid password."})
        
        # Existence checks
        df = pd.read_csv(FILE_NAME)

        # If username is found check if password matches, else send fail message
        # If username is found and password matches, send success message; else send fail message
        if user_data["username"] in df["Username"].values:
            user = df.loc[df["Username"] == user_data["username"]].iloc[0]
            if user_data["password"] == user["Password"]:
                session["current_user"] = user.to_dict()    # Stores information about the 'current user'
                print("Logged in user:", session["current_user"])
                return jsonify({"status": "success", "role": session["current_user"]["Role"], "message": f"User {session["current_user"]["Username"]} logged in."})
            else:
                return jsonify({"status": "fail", "message": "Incorrect username/password."})
        else:
            return jsonify({"status": "fail", "message": "Username does not exist."})

    return render_template("Login.html")


@app.route("/create-account", methods=["GET", "POST"])
def createUser():
    if request.method == "POST":
        user_data = request.get_json()

        # Empty field checks -- consider moving to client side
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


@app.route("/student")
def student():
    if "current_user" in session:
        return render_template("StudentPage.html")
    else:
        return redirect("/")


@app.route("/admin")
def admin():
    return render_template("AdminPage.html")


@app.route("/request-new-club", methods=["GET", "POST"])
def requestNewClub():
    if request.method == "POST":
        club_request_data = request.get_json()

        club_request_data["submittedBy"] = session["current_user"]["Username"]
        #print(club_request_data["submittedBy"]) # PRINTED GOOD

        # Empty field checks -- consider moving to client side
        if club_request_data["clubName"] == "":
            return jsonify({"status": "fail", "message": "Club name cannot be empty."})
        if club_request_data["topic"] == "":
            return jsonify({"status": "fail", "message": "Club topic cannot be empty."})
        if club_request_data["description"] == "":
            return jsonify({"status": "fail", "message": "Club description cannot be empty."})
        
        df = pd.read_csv("NewClubRequests.csv")

        if club_request_data["clubName"] in df["Club Name"].values:
            return jsonify({"status": "fail", "message": "Club with that name already exists."})

        csv_write_new_club_requests(club_request_data)

        #print("Received new club request:", club_request_data)
        return jsonify({"status": "success", "message": f"Request for {club_request_data["clubName"]} sent!"})
    
    return render_template("NewClubRequest.html")


if __name__ == "__main__":
    app.run(port=8080)