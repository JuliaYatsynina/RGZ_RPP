import os
import string
import secrets
from flask import Flask, request, redirect, jsonify
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, URL, Click

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't', 'y', 'yes']

db.init_app(app)
cache = Cache(app)
limiter = Limiter(app)


def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@app.route('/shorten', methods=['POST'])
@limiter.limit("10 per day", key_func=get_remote_address)
def shorten_url():
    data = request.json
    original_url = data.get('original_url')
    user_id = data.get('user_id')

    if not original_url:
        return jsonify({"error": "original_url is required"}), 400

    short_id = generate_short_id()
    new_url = URL(original_url=original_url, short_id=short_id, user_id=user_id)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({"short_id": short_id})


@app.route('/<short_id>', methods=['GET'])
@limiter.limit("100 per day", key_func=get_remote_address)
def redirect_to_url(short_id):
    url = URL.query.filter_by(short_id=short_id).first()
    if url:
        ip_address = request.remote_addr
        click = Click(url_id=url.id, ip_address=ip_address)
        db.session.add(click)
        db.session.commit()
        return redirect(url.original_url)
    return jsonify({"error": "URL not found"}), 404


@app.route('/stats/<short_id>', methods=['GET'])
def get_stats(short_id):
    url = URL.query.filter_by(short_id=short_id).first()
    if url:
        clicks = Click.query.filter_by(url_id=url.id).all()
        unique_ips = {click.ip_address for click in clicks}
        return jsonify({"clicks": len(clicks), "unique_ips": list(unique_ips)})
    return jsonify({"error": "URL not found"}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'])
