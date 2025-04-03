from extentions import db
from datetime import datetime


class IPRecord(db.Model):
    __tablename__ = "ip_records"

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    queried_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "country": self.country,
            "queried_at": self.queried_at.isoformat(),
        }
