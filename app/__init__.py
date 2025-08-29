import os
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Blueprint 登録
    from .feed.routes import feed_bp
    from .invest_clock.routes import invest_clock_bp
    from .ai_diagnosis.routes import ai_diagnosis_bp

    app.register_blueprint(feed_bp)
    app.register_blueprint(invest_clock_bp, url_prefix="/clock")
    app.register_blueprint(ai_diagnosis_bp, url_prefix="/ai")

    return app
