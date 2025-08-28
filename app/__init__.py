from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"  # AI診断で使うので必須

    # 各モジュールを登録
    from .feed.routes import feed_bp
    from .ai_diagnosis.routes import ai_bp
    from .invest_clock.routes import invest_clock_bp

    app.register_blueprint(feed_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(invest_clock_bp)

    return app
