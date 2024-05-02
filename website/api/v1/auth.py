import re
import secrets
import database
from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("api_auth", __name__, url_prefix="/auth")

def validate_token(user_id, auth_token):
    db = database.get_db()
    token = db.execute("SELECT auth_token, auth_user_id FROM auth WHERE auth_token = ? AND auth_user_id = ?", [auth_token, user_id]).fetchone()
    return token is not None

@bp.post("/login")
def api_auth_login():
    user_id = request.json.get("user_id", None)
    user_password = request.json.get("user_password", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id) or user_id is None or user_password is None:
        return { "logged_in": False, "error": "invalid username or password" }
    if not len(user_password) in range(6, 33):
        return { "logged_in": False, "error": "invalid username or password" }
    else:
        db = database.get_db()
        row = db.execute("SELECT user_id, user_password FROM users WHERE user_id = ?", [user_id]).fetchone()

        if row is not None and check_password_hash(row["user_password"], user_password):
            auth_token = secrets.token_hex()
            ip = request.remote_addr
            
            try: # remove old tokens (single user can use max 3 devices same time)
                tokens = db.execute("SELECT auth_token FROM auth WHERE user_id = ?", [user_id]).fetchall()
                if len(tokens) >= 3:
                    db.execute("DELETE FROM auth WHERE auth_token = ?", [tokens[0][0]])
            except:
                pass

            db.execute("INSERT INTO auth (auth_token, auth_user_id, auth_token_ip) VALUES (?, ?, ?)", [auth_token, user_id, ip])
            db.commit()

            return { "logged_in": True, "user_id": user_id, "auth_token": auth_token }
        else:
            return { "logged_in": False, "error": "invalid username or password" }


@bp.post("/logout")
def api_auth_logout():
    user_id = request.json.get("user_id", None)
    auth_token = request.json.get("auth_token", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id) or auth_token is None:
        return { "logged_out": False, "error": "invalid username" }
    else:
        logged_out = False

        db = database.get_db()
        db.execute("DELETE FROM auth WHERE auth_token = ? AND auth_user_id = ?", [auth_token, user_id])
        db.commit()
        logged_out = db.total_changes > 0
        
        return { "logged_out": logged_out }


@bp.post("/signup")
def api_auth_signup():
    user_id = request.json.get("user_id", None)
    user_password = request.json.get("user_password", None)
    user_mail = request.json.get("user_mail", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id) or user_id is None or user_password is None:
        return { "error": "invalid username" }
    if not len(user_password) in range(6, 33):
        return { "error": "invalid password length" }
    if not re.fullmatch(r'^[-\.\w]+@([-\w]+\.)+[-\w]{2,4}$', user_mail):
        return { "error": "invalid e-mail address" }
    else:
        db = database.get_db()
        if db.execute("SELECT * FROM users WHERE user_id = ?", [user_id]).fetchone() is not None:
            db.close()
            return { "error": "username already taken" }
        else:
            password_hash = generate_password_hash(user_password)
            
            db.execute("INSERT INTO users(user_id, user_password, user_mail) VALUES (?, ?, ?)", [user_id, password_hash, user_mail])
            db.commit()
            signed_up = db.total_changes > 0
            db.close()
            
            if signed_up:
                return { "signed_up": True }
            else:
                return { "error": "signup failed, please try again later" }

