import re
import uuid
import database
import requests
from flask import Blueprint, request
from api.v1.auth import validate_token

bp = Blueprint("api_clipboard", __name__, url_prefix="/clipboard")

def escape(html):
    return re.sub(r'<.*?>', '', html)

@bp.post("/add")
def api_clipboard_add():
    user_id = request.json.get("user_id", None)
    auth_token = request.json.get("auth_token", None)
    clip_data = request.json.get("clip_data", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id) or auth_token is None:
        return { "error": "bad request" }
    elif clip_data is None:
        return { "error": "bad data" }
    elif len(clip_data) > 2048:
        return { "error": "invalid data length" }
    else:
        clip_is_url = clip_data.startswith("http://") or clip_data.startswith("https://")

        if not validate_token(user_id, auth_token):
            return { "error": "authorization error" }
        
        data = {
            "clip_id": uuid.uuid4().hex,
            "clip_url": clip_data if clip_is_url else "",
            "clip_user_id": user_id,
            "clip_title": "",
            "clip_description": "" if clip_is_url else escape(clip_data),
            "clip_image": "",
            "clip_ip": request.remote_addr
        }

        if clip_is_url:
            try:
                ua = "Mozilla/5.0 (compatible; YandexBot/3.0; MirrorDetector; +http://yandex.com/bots)"
                content = requests.get(clip_data, headers={"user-agent": ua}).text

                def search_match(pattern, key, max_len=128, do_escape = False):
                    match = re.search(pattern, content, re.S | re.I)
                    if match is not None:
                        result = match.group(1).strip()[:max_len]
                        data[key] = escape(result) if do_escape else result

                search_match("<title>(.*?)</title>", "clip_title", 128, True)
                search_match('<meta property="og:title" content="([^"]+?)"', "clip_title", 128, True)
                search_match('<meta name="description" content="([^"]+?)"', "clip_description", 1024, True)
                search_match('<meta property="og:description" content="([^"]+?)"', "clip_description", 1024, True)
                search_match('<meta property="og:image" content="([^"]+?)"', "clip_image", 2048)

            except:
                pass

        column_names = ", ".join(data.keys())
        value_placeholders = ", ".join(list("?"*len(data.keys())))
        
        db = database.get_db()
        db.execute(f"INSERT INTO clipboard ({column_names}) VALUES ({value_placeholders})", list(data.values()))
        db.commit()

        row = db.execute("SELECT * FROM clipboard WHERE clip_id = ?", [data["clip_id"]]).fetchone()
    
        if row is not None:
            return {
                "clip_type": "url" if clip_is_url else "text",
                "clip_id": row["clip_id"],
                "clip_url": row["clip_url"],
                "clip_user_id": row["clip_user_id"],
                "clip_title": row["clip_title"],
                "clip_description": row["clip_description"],
                "clip_image": row["clip_image"],
                "clip_ip": row["clip_ip"],
                "clip_time": row["clip_time"]
            }
        else:
            return { "error": "an error occured, please try again" }

@bp.post("/list")
def api_clipboard_list():
    user_id = request.json.get("user_id", None)
    auth_token = request.json.get("auth_token", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id):
        return { "error": "bad request" }
    else:
        db = database.get_db()

        user = db.execute("SELECT user_id, content_is_public FROM users WHERE user_id = ?", [user_id]).fetchone()
        privacy = "public" if user[1] == 1 else "private"

        if privacy == "private" and not validate_token(user_id, auth_token):
            return { "error": "clipboard is private" }
        
        rows = db.execute("SELECT * FROM clipboard WHERE clip_user_id = ?", [user_id]).fetchall()

        return {
            "count": len(rows),
            "list": [ {
            "clip_type": "url" if len(row["clip_url"]) > 0 else "text",
            "clip_id": row["clip_id"],
            "clip_url": row["clip_url"],
            "clip_user_id": row["clip_user_id"],
            "clip_title": row["clip_title"],
            "clip_description": row["clip_description"],
            "clip_image": row["clip_image"],
            "clip_ip": row["clip_ip"],
            "clip_time": row["clip_time"]
        } for row in rows ]
        }


@bp.post("/delete")
def delete():
    user_id = request.json.get("user_id", None)
    auth_token = request.json.get("auth_token", None)
    clip_id = request.json.get("clip_id", None)

    if not re.fullmatch("[a-z0-9_]{4,24}", user_id) or auth_token is None:
        return { "error": "bad request" }
    else:
        db = database.get_db()
        
        if not validate_token(user_id, auth_token):
            db.close()
            return { "error": "authorization error" }
        
        db.execute("DELETE FROM clipboard WHERE clip_id = ?", [clip_id])
        db.commit()
        deleted = db.total_changes > 0

        return { "deleted": deleted, "clip_id": clip_id }

