import os
from flask import Flask
from .extensions import db, login_manager, csrf  # csrfを追加


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # -----------------------
    # 設定
    # -----------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myapp.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["WTF_CSRF_TIME_LIMIT"] = None  # CSRFトークンの有効期限（必要に応じて）

    # -----------------------
    # Extensions 初期化
    # -----------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    csrf.init_app(app)  # CSRF保護を有効化

    # -----------------------
    # Blueprints 登録
    # -----------------------
    from .auth.routes import auth_bp
    from .feed.routes import feed_bp
    from .invest_clock.routes import invest_clock_bp
    from .ai_diagnosis.routes import ai_diagnosis_bp
    from .posts.routes import post_bp
    from .bookshelf.routes import bookshelf_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(invest_clock_bp, url_prefix="/clock")
    app.register_blueprint(ai_diagnosis_bp, url_prefix="/ai")
    app.register_blueprint(post_bp)
    app.register_blueprint(bookshelf_bp)

    # -----------------------
    # DB初期化 / マイグレーションは別途使用
    # -----------------------
    # with app.app_context():
    #     db.create_all()  # Flask-Migrate 使う場合は不要

    return app
