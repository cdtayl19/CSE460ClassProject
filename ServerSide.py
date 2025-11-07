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

def write_approved_club_requests(approved_club_data):
    with open("ApprovedClubs.csv", 'a', newline='') as new_file:
        fieldnames = ['Submitted By', 'Club Name', 'Topic', 'Details', 'Members', 'Events']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(approved_club_data)

def write_messages(message):
    with open("Messages.csv", 'a', newline='') as new_file:
        fieldnames = ['To', 'From', 'Topic', 'Message']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(message)

# Server Stuff
app = Flask(__name__)
app.secret_key = "32895"

# Logs out of the app
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# Change route to get-current-user
# Sets the current user.
@app.route("/current-user", methods=["GET", "POST"])
def get_current_user():
    if request.method == "GET":
        if "current_user" in session:
            return jsonify({"status": "success", "user": session["current_user"]})
        else:
            return jsonify({"status": "fail", "message": "No user logged in."})


# Change route to get-club-requests
# Returns number of entries in NewClubRequests.csv
@app.route("/club-requests", methods=["GET", "POST"])
def get_club_requests():
    if request.method == "GET":
        df = pd.read_csv("NewClubRequests.csv")
        return jsonify({"status": "success", "number": len(df)})


@app.route("/get-messages", methods=["GET"])
def get_messages():
    if request.method == "GET":
        df = pd.read_csv("Messages.csv")
        user_messages = df[df["To"] == session["current_user"]["Username"]]
        print(user_messages)
        return jsonify({"status": "success", "number": len(user_messages)})
    


# Login Page
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


# Returns individual entry from NewClubRequests.csv
@app.route("/get-club-request", methods=["GET"])
def get_club_request():
    # Retrieves index from arguments sent by fetch(`/get-club-request?index=${index}`
    index = request.args.get("index", type=int)
    #print(f"Index: {index}")

    # Creates dataframe from csv
    df = pd.read_csv("NewClubRequests.csv")
    #print(f"DF Length: {len(df)}")

    # Returns 'No new requests' if NewClubRequests.csv is empty
    if len(df) == 0:
        return jsonify({"status": "fail", "message": "No new requests."})
    
    # Returns dataframe row at specified index
    if 0 <= index < len(df): 
        return jsonify({"status": "success", "index": index, "data": df.loc[index].to_dict()})
    
    # Wraps back around to first entry if index > dataframe length. When using nextBtn
    if index >= len(df):
        return jsonify({"status": "success", "index": 0, "data": df.loc[0].to_dict()})
    
    # Wraps back around to last entry row if index < 0. When using prevBtn
    if index < 0:
        return jsonify({"status": "success", "index": len(df) - 1, "data": df.loc[len(df) - 1].to_dict()})


@app.route("/get-message", methods=["GET", "POST"])
def get_message():
    if request.method == "GET":
        index = request.args.get("index", type=int)
        df = pd.read_csv("Messages.csv")
        
        if len(df) == 0:
            return jsonify({"status": "fail", "message": "No new messages."})   
        
        if 0 <= index < len(df): 
            return jsonify({"status": "success", "index": index, "data": df.loc[index].to_dict()})
        
        if index >= len(df):
            return jsonify({"status": "success", "index": 0, "data": df.loc[0].to_dict()})
        
        if index < 0:
            return jsonify({"status": "success", "index": len(df) - 1, "data": df.loc[len(df) - 1].to_dict()})
        
@app.route("/delete-message", methods=["POST"])
def delete_message():
    if request.method == "POST":
        data = request.get_json()

        # Remove approved club from requests
        df = pd.read_csv("Messages.csv")
        df = df[df["Message"] != data["message"]]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("Messages.csv", index=False)
        #print(f"DF Length: {len(df)}")
        return jsonify({"status": "success", "message": "Message deleted.", "length": len(df)})
    

@app.route("/approve-club-request", methods=["GET", "POST"])
def approveRequest():
    if request.method == "POST":
        approved_data = request.get_json()
        
        # Send club data to approved.csv
        approved_data = request.get_json()
        holder = {
            "Submitted By": approved_data["user"], 
            "Club Name": approved_data["name"], 
            "Topic": approved_data["topic"], 
            "Details": approved_data["description"], 
            "Members": "None", 
            "Events": "None"
        }
        write_approved_club_requests(holder)
        
        # Remove approved club from requests
        df = pd.read_csv("NewClubRequests.csv")
        df = df[df["Club Name"] != approved_data["name"]]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("NewClubRequests.csv", index=False)
        #print(f"DF Length: {len(df)}")

        # Send message to student who submitted club request
        message = {"To": approved_data["user"], "From": session["current_user"]["Username"], "Message":f"Your club request for {approved_data["name"]} has been approved!"}
        write_messages(message)

        # Return 'empty' message by default. If not really empty html file corrects and displays the correct screen.
        # However empty display remains if final/only request is approved. 
        return jsonify({"status": "fail", "message": "No new requests.", "length": len(df)})

@app.route("/deny-club-request", methods=["GET", "POST"])
def denyRequest():
    if request.method == "POST":
        denied_data = request.get_json()

        # Remove approved club from requests
        df = pd.read_csv("NewClubRequests.csv")
        df = df[df["Club Name"] != denied_data["name"]]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("NewClubRequests.csv", index=False)
        #print(f"DF Length: {len(df)}")

        # Send message to student who submitted club request
        message = {"To": denied_data["user"], "From": session["current_user"]["Username"], "Message":f"Your club request for {denied_data["name"]} has been rejected."}
        write_messages(message)

        # Return 'empty' message by default. If not really empty html file corrects and displays the correct screen.
        # However empty display remains if final/only request is approved. 
        return jsonify({"status": "fail", "message": "No new requests.", "length": len(df)})
        


# Adds entry to User_Accounts.csv
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


# Displays student page tailored to current user
@app.route("/student")
def student():
    if "current_user" in session:
        return render_template("StudentPage.html")
    else:
        return redirect("/")


# Displays admin page tailored to current user
@app.route("/admin")
def admin():
    if "current_user" in session:
        return render_template("AdminPage.html")
    else:
        return redirect("/")
    

# Adds entry to NewClubRequests.csv
@app.route("/request-new-club", methods=["GET", "POST"])
def requestNewClub():
    if request.method == "POST":

        # Retrieve data from user request
        club_request_data = request.get_json()

        # Sets submittedBy field to current user
        club_request_data["submittedBy"] = session["current_user"]["Username"]

        # Empty field checks -- consider moving to client side
        if club_request_data["clubName"] == "":
            return jsonify({"status": "fail", "message": "Club name cannot be empty."})
        if club_request_data["topic"] == "":
            return jsonify({"status": "fail", "message": "Club topic cannot be empty."})
        if club_request_data["description"] == "":
            return jsonify({"status": "fail", "message": "Club description cannot be empty."})
        
        # Creates dataframe from NewClubRequests.csv
        df = pd.read_csv("NewClubRequests.csv")

        # Will no add new club, if club name already exists. 
        if club_request_data["clubName"] in df["Club Name"].values:
            return jsonify({"status": "fail", "message": "Club with that name already exists."})

        # Writes new club request to NewClubRequests.csv
        csv_write_new_club_requests(club_request_data)

        return jsonify({"status": "success", "message": f"Request for {club_request_data["clubName"]} sent!"})
    
    return render_template("NewClubRequest.html")


# View Club Requests Page
@app.route("/view-club-requests", methods=["GET", "POST"])
def viewClubRequests():
    return render_template("ViewclubRequests.html")

@app.route("/view-messages", methods=["GET"])
def viewMessages():
    return render_template("viewMessages.html")


if __name__ == "__main__":
    app.run(port=8080)