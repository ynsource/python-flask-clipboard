import re
import database
from flask import Blueprint, request
from api.v1.auth import validate_token

bp = Blueprint("api_user", __name__, url_prefix="/user")

def get_user_privacy(user_id):
    db = database.get_db()
    row = db.execute("SELECT user_id, content_is_public FROM users WHERE user_id = ?", [user_id]).fetchone()
    if row is not None:
        return "public" if row is not None and row["content_is_public"] == 1 else "private"
    else:
        return None

@bp.post("/privacy")
def api_user_privacy():
    user_id = request.json.get("user_id", None)
    auth_token = request.json.get("auth_token", None)
    set_privacy = request.json.get("privacy", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id) or auth_token is None:
        return { "error": "bad request" }
    else:
        if not validate_token(user_id, auth_token):
            return { "error": "authorization error" }
        
        privacy = None

        if set_privacy in ("public", "private"):
            db = database.get_db()
            privacy_value = 1 if set_privacy == "public" else 0
            db.execute("UPDATE users SET content_is_public = ? WHERE user_id = ?", [privacy_value, user_id])
            db.commit()
            if db.total_changes > 0:
                privacy = set_privacy
        else:
            privacy = get_user_privacy(user_id)

        if privacy is None:
            return { "error": "an error occured, please try again later" }
        else:
            return { "privacy": privacy }

