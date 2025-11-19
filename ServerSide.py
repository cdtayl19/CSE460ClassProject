from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
import csv
import json

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
        fieldnames = ['Leader', 'Club Name', 'Topic', 'Details', 'Members', 'Events']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(approved_club_data)

def write_messages(message):
    with open("Messages.csv", 'a', newline='') as new_file:
        fieldnames = ['To', 'From', 'Message']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(message)

def write_join_club_requests(message):
    with open("JoinRequests.csv", 'a', newline='') as new_file:
        fieldnames = ['Student', 'Leader', 'Club Name']
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writerow(message)

def write_events(message):
    with open("Events.csv", 'a', newline='') as new_file:
        fieldnames = ['Club Name', 'Event Name', 'Date', 'Time', 'Location', 'Description', 'Max Guests', 'Registered Guests']
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


# Later, change route to get-current-user
# Sets the current user.
@app.route("/current-user")
def get_current_user():
    if "current_user" in session:
        return jsonify({"status": "success", "user": session["current_user"]})
    else:
        return jsonify({"status": "fail", "message": "No user logged in."})


# Later, change route to get-club-requests
# Returns number of entries in NewClubRequests.csv
@app.route("/club-requests")
def get_club_requests():
    df = pd.read_csv("NewClubRequests.csv")
    return jsonify({"status": "success", "number": len(df)})


# Gets the number of messages in Messages.csv
@app.route("/get-messages")
def get_messages():
    df = pd.read_csv("Messages.csv")
    user_messages = df[df["To"] == session["current_user"]["Username"]]
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
                return jsonify({"status": "success", "role": session["current_user"]["Role"], "message": f"User {session["current_user"]["Username"]} logged in."})
            else:
                return jsonify({"status": "fail", "message": "Incorrect username/password."})
        else:
            return jsonify({"status": "fail", "message": "Username does not exist."})

    return render_template("Login.html")


# Returns individual entry from NewClubRequests.csv
@app.route("/get-club-request")
def get_club_request():
    # Retrieves index from arguments
    index = request.args.get("index", type=int)

    # Creates dataframe from csv
    df = pd.read_csv("NewClubRequests.csv")

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


# Gets a single message by its index
@app.route("/get-message")
def get_message():

    # Retrieves index from arguments 
    index = request.args.get("index", type=int)

    # Creates dataframe from csv
    df = pd.read_csv("Messages.csv")
        
    # Empty check
    if len(df) == 0:
        return jsonify({"status": "fail", "message": "No new messages."})   
        
    # Valid index
    if 0 <= index < len(df): 
        return jsonify({"status": "success", "index": index, "data": df.loc[index].to_dict()})
        
    # Next button wrap around
    if index >= len(df):
        return jsonify({"status": "success", "index": 0, "data": df.loc[0].to_dict()})
        
    # Prev button wrap around
    if index < 0:
        return jsonify({"status": "success", "index": len(df) - 1, "data": df.loc[len(df) - 1].to_dict()})
        

# Removes message from Messages.csv
@app.route("/delete-message", methods=["POST"])
def delete_message():
    if request.method == "POST":
        data = request.get_json()

        # Remove message
        df = pd.read_csv("Messages.csv")
        df = df[df["Message"] != data["message"]]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("Messages.csv", index=False)

        return jsonify({"status": "success", "message": "Message deleted.", "length": len(df)})
    

# Adds club to ApprovedClubs.csv
@app.route("/approve-club-request", methods=["POST"])
def approveRequest():
    if request.method == "POST":
        approved_data = request.get_json()
        
        # Send club data to approved.csv
        # Adds fields 'members' & 'events' needed for later
        approved_data = request.get_json()
        holder = {
            "Leader": approved_data["user"], 
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

        # Send message to student who submitted club request
        message = {"To": approved_data["user"], "From": session["current_user"]["Username"], "Message":f"Your club request for {approved_data["name"]} has been approved!"}
        write_messages(message)

        # Return 'empty' message by default. If not really empty html file corrects and displays the correct screen.
        # However empty display remains if final/only request is approved. 
        return jsonify({"status": "fail", "message": "No new requests.", "length": len(df)})


# Removes club request from NewClubRequests.csv
@app.route("/deny-club-request", methods=["POST"])
def denyRequest():
    if request.method == "POST":
        denied_data = request.get_json()

        # Remove approved club from requests
        df = pd.read_csv("NewClubRequests.csv")
        df = df[df["Club Name"] != denied_data["name"]]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("NewClubRequests.csv", index=False)

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
@app.route("/view-club-requests")
def viewClubRequests():
    return render_template("ViewclubRequests.html")


@app.route("/view-messages")
def viewMessages():
    return render_template("ViewMessages.html")

@app.route("/view-join-requests")
def viewRequests():
    return render_template("ViewJoinRequests.html")


@app.route("/browse-clubs")
def browseClubs():
    return render_template("ClubListings.html")

@app.route("/browse-events")
def browseEvents():
    return render_template("EventListings.html")


@app.route("/get-clubs")
def getClubs():
    df = pd.read_csv("ApprovedClubs.csv")
    
    if df.empty:
        return jsonify({"status": "fail", "message": "No approved clubs found."})
    
    clubs = json.loads(df.to_json(orient="records"))
    return jsonify({"status": "success", "clubs": clubs})

@app.route("/get-events")
def getEvents():
    df = pd.read_csv("Events.csv")
    
    if df.empty:
        return jsonify({"status": "fail", "message": "No events found."})
    
    events = json.loads(df.to_json(orient="records"))
    return jsonify({"status": "success", "events": events})


@app.route("/club-page")
def clubPage():
    club_name = request.args.get("name")
    df = pd.read_csv("ApprovedClubs.csv")
    club = df[df["Club Name"] == club_name]
    club_info = club.iloc[0].to_dict()

    return render_template("ClubPage.html", club=club_info)

@app.route("/event-page")
def eventPage():
    event_name = request.args.get("name")
    df = pd.read_csv("Events.csv")
    event = df[df["Event Name"] == event_name]
    event_info = event.iloc[0].to_dict()

    return render_template("EventPage.html", event=event_info)


@app.route("/send-join-request", methods=["POST"])
def sendJoinRequest():
    if request.method == "POST":
        join_request_data = request.get_json()        

        join_request_from   = join_request_data["user"]["Username"]
        join_request_to     = join_request_data["leader"]
        join_request_club   = join_request_data["clubName"]

        join_request_message = {"Student": join_request_from, "Leader": join_request_to, "Club Name": join_request_club}

        write_join_club_requests(join_request_message)

    return jsonify({"status": "success"})

# Gets the number of join requests in JoinRequests.csv
@app.route("/get-join-requests")
def get_join_requests():
    club_name = request.args.get("club")
    df = pd.read_csv("JoinRequests.csv")
    join_requests = df[df["Club Name"] == club_name]
    return jsonify({"status": "success", "number": len(join_requests)})


# Gets the number of Registered Guests of an Event
@app.route("/get-registered-guests")
def get_registered_guests():
    event_name = request.args.get("event")
    
    df = pd.read_csv("Events.csv", na_values=["", "None", "nan", "NaN"])
    event = df[df["Event Name"] == event_name]

    # Must convert to int. Else improper JSON error. 
    max_guests = int(event.iloc[0]["Max Guests"])

    current_guests = event.iloc[0]["Registered Guests"]

    if pd.isna(current_guests):
        registered_guests = []
    else:
        registered_guests = json.loads(event.iloc[0]["Registered Guests"])
    
    return jsonify({"status": "success", "max": max_guests,  "number": len(registered_guests)})


@app.route("/get-join-request")
def get_request():
    index = request.args.get("index", type=int)
    club_name  = request.args.get("name")
    
    df = pd.read_csv("JoinRequests.csv")
    club_requests = df[df["Club Name"] == club_name].reset_index(drop=True)
    
    # Empty check
    if len(club_requests) == 0:
        return jsonify({"status": "fail", "message": "No new requests."})   
        
    # Valid index
    if 0 <= index < len(club_requests): 
        return jsonify({"status": "success", "index": index, "data": club_requests.loc[index].to_dict()})
        
    # Next button wrap around
    if index >= len(club_requests):
        return jsonify({"status": "success", "index": 0, "data": club_requests.loc[0].to_dict()})
        
    # Prev button wrap around
    if index < 0:
        return jsonify({"status": "success", "index": len(club_requests) - 1, "data": club_requests.loc[len(club_requests) - 1].to_dict()})


@app.route("/approve-join-request", methods=["POST"])
def approve_join():
    if request.method == "POST":
        approved_data = request.get_json()

        # Tells pandas that "Members" is type string
        # Lists options for empty values
        df = pd.read_csv("ApprovedClubs.csv", dtype={"Members": str}, na_values=["", "None", "nan", "NaN"])

        idx = df.index[df["Club Name"] == approved_data["club"]][0]

        current_members = df.at[idx, "Members"]
    
        if pd.isna(current_members) or current_members in ["", "None"]:
            members_list = []
        else:
            members_list = json.loads(current_members)
        
        if approved_data["student"] not in members_list:
            members_list.append(approved_data["student"])

        df.at[idx, "Members"] = json.dumps(members_list)
        df.to_csv("ApprovedClubs.csv", index=False)

        # Remove approved request from requests
        df = pd.read_csv("JoinRequests.csv")
        df = df[~((df["Student"] == approved_data["student"]) & (df["Club Name"] == approved_data["club"]))]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("JoinRequests.csv", index=False)

        # Send message to student who submitted join request
        message = {"To": approved_data["student"], "From": session["current_user"]["Username"], "Message":f"Your club request for {approved_data["club"]} has been approved!"}
        write_messages(message)

        # Return 'empty' message by default. If not really empty html file corrects and displays the correct screen.
        # However empty display remains if final/only request is approved. 
        return jsonify({"status": "fail", "message": "No new requests.", "length": len(df)})


@app.route("/register-guest", methods=["POST"])
def register_guest():
    if request.method == "POST":
        event_data = request.get_json()

        # Tells pandas that "Registered Guests" is type string
        # Lists options for empty values
        df = pd.read_csv("Events.csv", dtype={"Registered Guests": str}, na_values=["", "None", "nan", "NaN"])

        idx = df.index[df["Event Name"] == event_data["eventName"]][0]

        current_guests = df.at[idx, "Registered Guests"]
    
        if pd.isna(current_guests) or current_guests in ["", "None"]:
            guest_list = []
        else:
            guest_list = json.loads(current_guests)
        
        if event_data["user"]["Username"] not in guest_list:
            guest_list.append(event_data["user"]["Username"])

        df.at[idx, "Registered Guests"] = json.dumps(guest_list)
        df.to_csv("Events.csv", index=False)

        
        # Send message to student who submitted join request
        #message = {"To": event_data["Username"], "From": session["current_user"]["Username"], "Message":f"Your club request for {event_data["club"]} has been approved!"}
        #write_messages(message)

       
        return jsonify({"status": "success"})


@app.route("/deny-join-request", methods=["POST"])
def deny_join():
    if request.method == "POST":
        denied_data = request.get_json()

        # Remove approved club from requests
        df = pd.read_csv("JoinRequests.csv")
        df = df[~((df["Student"] == denied_data["student"]) & (df["Club Name"] == denied_data["club"]))]
        df.reset_index(drop=True, inplace=True)
        df.to_csv("JoinRequests.csv", index=False)

        # Send message to student who submitted club request
        message = {"To": denied_data["student"], "From": session["current_user"]["Username"], "Message":f"Your club request for {denied_data["club"]} has been denied."}
        write_messages(message)

        # Return 'empty' message by default. If not really empty html file corrects and displays the correct screen.
        # However empty display remains if final/only request is approved. 
        return jsonify({"status": "fail", "message": "No new requests.", "length": len(df)})


@app.route("/create-event", methods=["GET", "POST"])
def create_event():
    if request.method == "POST":
        event_data = request.get_json()

        # Empty field checks -- consider moving to client side
        if event_data["eventName"] == "":
            return jsonify({"status": "fail", "message": "Event name cannot be empty."})
        if event_data["date"] == "":
            return jsonify({"status": "fail", "message": "Date name cannot be empty."})
        if event_data["time"] == "":
            return jsonify({"status": "fail", "message": "Time cannot be empty."})
        if event_data["location"] == "":
            return jsonify({"status": "fail", "message": "Location cannot be empty."})
        
        if event_data["maxGuests"] == "":
            return jsonify({"status": "fail", "message": "Max guests cannot be empty."})
        if not event_data["maxGuests"].isdigit():
            return jsonify({"status": "fail", "message": "Max guests must be a valid integer."})
        if int(event_data["maxGuests"]) <= 0:
            return jsonify({"status": "fail", "message": "Max guests must be a positive number."})
        
        if event_data["description"] == "":
            return jsonify({"status": "fail", "message": "Description cannot be empty."})
        
        # Existing event checks
        df = pd.read_csv("Events.csv")

        # Existing event check by name
        if event_data["eventName"] in df["Event Name"].values:
           return jsonify({"status": "fail", "message": "Event with that name already exists."})
        
        holder = {
            "Club Name": event_data["clubName"], 
            "Event Name": event_data["eventName"], 
            "Date": event_data["date"], 
            "Time": event_data["time"],
            "Location": event_data["location"],
            "Description": event_data["description"],
            "Max Guests": event_data["maxGuests"]
        }
        
        # Send user data to csv for storage
        write_events(holder)

        add_event_to_club(holder)

        return jsonify({"status": "success"})
    return render_template("CreateEvent.html")


def add_event_to_club(club_event):

    # Tells pandas that "Members" is type string
    # Lists options for empty values
    df = pd.read_csv("ApprovedClubs.csv", dtype={"Events": str}, na_values=["", "None", "nan", "NaN"])

    idx = df.index[df["Club Name"] == club_event["Club Name"]][0]

    current_events = df.at[idx, "Events"]
    
    if pd.isna(current_events) or current_events in ["", "None"]:
        events_list = []
    else:
        events_list = json.loads(current_events)
        
    if club_event["Event Name"] not in events_list:
        events_list.append(club_event["Event Name"])

    df.at[idx, "Events"] = json.dumps(events_list)
    df.to_csv("ApprovedClubs.csv", index=False)


@app.route("/manage-club", methods=["POST"])
def manage_club():
    if request.method == "POST":
        update_data = request.get_json()
        club_name = update_data["club"]

        # Change club Leader
        if update_data["leader"] != "":
            df = pd.read_csv("User_Accounts.csv")

            if update_data["leader"] not in df["Username"].values:
                return jsonify({"status": "fail", "message": "Username does not exist."})
            else:
                df = pd.read_csv("ApprovedClubs.csv")
                df.loc[df["Club Name"] == club_name, "Leader"] = update_data["leader"]
                df.to_csv("ApprovedClubs.csv", index=False)
                return jsonify({"status": "success", "leader": update_data["leader"]})
            
        # Change club Topic
        if update_data["topic"] != "":
            df = pd.read_csv("ApprovedClubs.csv")
            df.loc[df["Club Name"] == club_name, "Topic"] = update_data["topic"]
            df.to_csv("ApprovedClubs.csv", index=False)
            return jsonify({"status": "success", "topic": update_data["topic"]})
        
        # Change club Details
        if update_data["details"] != "":
            df = pd.read_csv("ApprovedClubs.csv")
            df.loc[df["Club Name"] == club_name, "Details"] = update_data["details"]
            df.to_csv("ApprovedClubs.csv", index=False)
            return jsonify({"status": "success", "details": update_data["details"]})
        
        # Remove Member
        if update_data["member"] != "":
            df = pd.read_csv("ApprovedClubs.csv")

            idx = df.index[df["Club Name"] == update_data["club"]][0]
            current_members = df.at[idx, "Members"]
            
            if pd.isna(current_members):
                return jsonify({"status": "fail", "message": "Club has no members to remove."})
            else:
                current_members = json.loads(current_members)

                if update_data["member"] not in current_members:
                    return jsonify({"status": "fail", "message": "Member not found in club."})
                else:
                    current_members.remove(update_data["member"])
                    df.at[idx, "Members"] = json.dumps(current_members)
                    df.to_csv("ApprovedClubs.csv", index=False)
                    return jsonify({"status": "success", "message": "Member removed."})
        
        # Cancel Event
        if update_data["event"] != "":
            df = pd.read_csv("ApprovedClubs.csv")

            idx = df.index[df["Club Name"] == update_data["club"]][0]
            current_events = df.at[idx, "Events"]
            
            if pd.isna(current_events):
                return jsonify({"status": "fail", "message": "Club has no events to remove."})
            else:
                current_events = json.loads(current_events)

                if update_data["event"] not in current_events:
                    return jsonify({"status": "fail", "message": "Event not found."})
                else:
                    current_events.remove(update_data["event"])
                    df.at[idx, "Events"] = json.dumps(current_events)
                    df.to_csv("ApprovedClubs.csv", index=False)
                    return jsonify({"status": "success", "message": "Event canceled."})

        # Change club Name
        if update_data["name"] != "":
            df = pd.read_csv("ApprovedClubs.csv")

            if update_data["name"] in df["Club Name"].values:
                return jsonify({"status": "fail", "message": "Club name already exists."})
            else:
                df.loc[df["Club Name"] == club_name, "Club Name"] = update_data["name"]
                df.to_csv("ApprovedClubs.csv", index=False)
                return jsonify({"status": "success", "name": update_data["name"]})

        return jsonify({"status": "fail", "message": "No input given."})


@app.route("/get-club-leader")
def get_leader():
    club_name = request.args.get("club")
    #print(club_name)

    df = pd.read_csv("ApprovedClubs.csv")
    
    leader = df.loc[df["Club Name"] == club_name, "Leader"].iloc[0]
    print(f"The leader is: {leader}")

    return jsonify({"status": "success", "leader": leader})





if __name__ == "__main__":
    app.run(port=8080)