from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api', methods=["GET"])
def greet():
    return jsonify({"message": "bye"})

if __name__ == "__main__":
    app.run(port=8080)