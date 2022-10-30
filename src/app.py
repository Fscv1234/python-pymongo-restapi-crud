from flask import Flask, jsonify, make_response, request
import logging
import os
from flask_session import Session
from routes.Login import Login
from routes.Ticket import Ticket

app = Flask(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
print("PATH")
print(PROJECT_ROOT)

app.secret_key = "secretkey"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECURE"] = True
app.config["PATH_FILE"] = os.path.join(PROJECT_ROOT, "src", "file")
app.config["DSN_PSQL"] = "host=172.18.0.3 dbname=my_db user=postgres password=postgres port=5432"
handler = logging.FileHandler(
    os.path.join(PROJECT_ROOT, "src", "file", "app.log")
)  # errors logged to this file
handler.setLevel(logging.ERROR)  # only log errors and above
app.logger.addHandler(handler)  # attach the handler to the app's logger
Session(app)

app.register_blueprint(Login)
app.register_blueprint(Ticket)


@app.route("/", methods=["GET"])
def index():
    return make_response(jsonify({"message": "OKEY FROM API"}), 200)


@app.errorhandler(404)
def not_found(error=None):
    return make_response(
        jsonify({"ok": 1, "message": "Resource Not Found please, " + request.url}), 200
    )


if __name__ == "__main__":
    app.run(debug=True, port=3000)
