from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from modles.user import User
import datetime
from extentions import limiter
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/auth.log",
)
logger = logging.getLogger("auth")

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing request body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({"error": "Invalid username or password"}), 401

    if not user.is_approved:
        return jsonify({"error": "Account is pending approval"}), 401

    expires = datetime.timedelta(hours=24)
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
        expires_delta=expires,
    )

    logger.info(f"Successful login for user: {username}")
    return jsonify({"access_token": access_token, "user": user.to_dict()}), 200
