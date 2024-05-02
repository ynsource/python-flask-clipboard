from flask import Blueprint
import api.v1
import api.v1.auth
import api.v1.clipboard
import api.v1.user

bp = Blueprint("api_v1", __name__, url_prefix="/v1")

bp.register_blueprint(api.v1.user.bp)
bp.register_blueprint(api.v1.auth.bp)
bp.register_blueprint(api.v1.clipboard.bp)

@bp.get("/")
def api_summary():
    return {
        "name": "Clipboard - YNSource",
        "summary": "This is an example API with Python/Flask",
        "version": "1.0.0"
    }

