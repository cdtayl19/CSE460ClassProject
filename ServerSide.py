from flask import Flask, render_template, request, jsonify
import csv


# CSV Stuff
FILE_NAME = "User_Accounts.csv"


# Server Stuff
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("Login.html")

@app.route("/create-account", methods=["GET", "POST"])
def createUser():
    if request.method == "POST":
        user_data = request.get_json()

        # Send user data to csv for storage
        with open(FILE_NAME, 'a', newline='') as new_file:
            fieldnames = ['firstname', 'lastname', 'email', 'username', 'password', 'role']
            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')
            csv_writer.writerow(user_data)

        print("Received new account:", user_data)
        return jsonify({"status": "success", "message": f"User {user_data["username"]} created!"})
    
    return render_template("CreateUser.html")

if __name__ == "__main__":
    app.run(port=8080)