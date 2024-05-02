import re
import apis
import database
from flask import Flask, request, render_template, redirect, url_for, json
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.register_blueprint(apis.bp)
app.teardown_appcontext(database.close_db)

@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    response = e.get_response()
    if request.path.startswith("/api"):
        response.content_type = "application/json"
        response.data = json.dumps({
            "error": {
                "code": e.code,
                "name": e.name,
                "description": e.description
            }
        })
    return response

@app.get("/")
def index():
    user_id = request.cookies.get("user_id", None)
    auth_token = request.cookies.get("auth_token", None)
    if user_id is None or auth_token is None:
        return redirect(url_for('login'))
    else:
        from api.v1.user import get_user_privacy
        return render_template("index.html", user_id = user_id, user_privacy = get_user_privacy(user_id))

@app.get("/login")
def login():
    return render_template("login.html", sign_up = False)

@app.get("/signup")
def signup():
    return render_template("login.html", sign_up = True)

@app.get("/u/<string:user_id>")
def user_page(user_id):
    if not re.fullmatch("[a-z0-9_]{4,24}", user_id):
        return "User not found or this account was deleted!"
    else:
        db = database.get_db()
        data = db.execute("SELECT user_id, content_is_public FROM users WHERE user_id = ?", [user_id]).fetchone()
        db.close()

        if data is None:
            return render_template("error.html", msg="User not found or this account was deleted!")
        else:
            privacy = "public" if data[1] == 1 else "private"
            if privacy == "public":
                return render_template("clipboard.html", user_id = user_id)
            else:
                return render_template("error.html", msg="This clipboard is private!")
