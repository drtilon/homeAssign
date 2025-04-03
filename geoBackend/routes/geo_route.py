from flask import Blueprint, request, jsonify
import requests
from flask_jwt_extended import jwt_required
import ipaddress
import logging
from datetime import datetime
from modles.ip_record import IPRecord
from extentions import db
from extentions import limiter

geo_bp = Blueprint("geo", __name__, url_prefix="/api/geo")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/geo_api.log",
)
logger = logging.getLogger("geo")


def is_valid_ip(ip):
    """Validate if the string is a valid IPv4 or IPv6 address"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def parse_date_param(date_str):
    """Parse ISO date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


@geo_bp.route("/country/<string:country_name>/ips", methods=["GET"])
@jwt_required()
def get_ips_by_country(country_name):
    start_date = parse_date_param(request.args.get("start_date"))
    end_date = parse_date_param(request.args.get("end_date"))

    query = IPRecord.query.filter(IPRecord.country.ilike(f"%{country_name}%"))

    if start_date:
        query = query.filter(IPRecord.queried_at >= start_date)
    if end_date:
        query = query.filter(IPRecord.queried_at <= end_date)

    records = query.order_by(IPRecord.queried_at.desc()).all()

    if not records:
        return jsonify(
            {
                "error": f"No IP records found for country '{country_name}'",
                "country": country_name,
            }
        ), 404

    return jsonify(
        {
            "country": country_name,
            "ip_count": len(records),
            "ips": [
                {
                    "ip_address": record.ip_address,
                    "queried_at": record.queried_at.isoformat(),
                }
                for record in records
            ],
        }
    ), 200


@geo_bp.route("/lookup", methods=["GET"])
@jwt_required()
def lookup_ip():
    ip_address = request.args.get("ip")

    if not ip_address:
        return jsonify({"error": "Missing IP address parameter"}), 400

    if not is_valid_ip(ip_address):
        logger.warning(f"Invalid IP format submitted: {ip_address}")
        return jsonify({"error": "Invalid IP address format"}), 400

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode",
            timeout=5,
        )
        data = response.json()

        if data.get("status") == "success":
            country = data.get("country", "Unknown")

            try:
                ip_record = IPRecord(ip_address=ip_address, country=country)
                db.session.add(ip_record)
                db.session.commit()
                logger.info(f"Stored IP lookup: {ip_address} -> {country}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to store IP record: {str(e)}")

            return jsonify({"ip": ip_address, "country": country}), 200
        else:
            return jsonify(
                {"error": "Could not determine location for IP address"}
            ), 404

    except requests.Timeout:
        return jsonify({"error": "External geolocation service timeout"}), 504
    except Exception as e:
        logger.error(f"Error looking up IP location: {str(e)}")
        return jsonify({"error": "Server error processing geolocation request"}), 500


@geo_bp.route("/top-countries", methods=["GET"])
@jwt_required()
def get_top_countries():
    start_date = parse_date_param(request.args.get("start_date"))
    end_date = parse_date_param(request.args.get("end_date"))

    limit = min(request.args.get("limit", default=5, type=int), 50)

    from sqlalchemy import func

    query = db.session.query(
        IPRecord.country, func.count(IPRecord.country).label("request_count")
    ).group_by(IPRecord.country)

    if start_date:
        query = query.filter(IPRecord.queried_at >= start_date)
    if end_date:
        query = query.filter(IPRecord.queried_at <= end_date)

    top_countries = (
        query.order_by(func.count(IPRecord.country).desc()).limit(limit).all()
    )

    result = {
        "total_countries": len(top_countries),
        "countries": [
            {"country": country, "request_count": count}
            for country, count in top_countries
        ],
    }

    return jsonify(result), 200
