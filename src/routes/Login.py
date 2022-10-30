from sys import stderr
from flask import (
    Blueprint,
    flash,
    request,
    render_template,
    redirect,
    url_for,
    session,
)

# from mongodb import connect
# UserRepository = connect("user")
Login = Blueprint("Login", __name__)


@Login.route("/login", methods=["GET", "POST"])
def login():
    users = {"caja1": "parrillada", "caja2": "pollada", "admin": "admin"}
    ids = {"caja1": 0, "caja2": 1}
    error = None
    user = {"id": 0, "name": "INVITADO", "is_authenticated": False}
    if request.method == "POST":
        print("---DATA", file=stderr)
        data = request.form.to_dict()
        print(data, file=stderr)
        if users.get(data["document"]) is None:
            flash("Error document not defined")
        if users[data["document"]] != data["password"]:
            flash("Error password")
        user = {
            "id": ids[data["document"]],
            "name": users[data["document"]],
            "is_authenticated": True,
        }
        session["current_user"] = user
        return redirect(url_for("Ticket.tickets"))
    print("---SESSION IN", file=stderr)
    print(session, file=stderr)
    return render_template("login.html", title="login", current_user=user, error=error)


@Login.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("Login.login"))
