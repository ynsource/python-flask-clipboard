from flask import Blueprint, redirect
import api_v1

bp = Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(api_v1.bp)

@bp.get("/")
def api_version_redirect():
    return redirect("/api/v1")

