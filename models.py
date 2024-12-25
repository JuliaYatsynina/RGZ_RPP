from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_id = db.Column(db.String(6), unique=True, nullable=False)
    user_id = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
