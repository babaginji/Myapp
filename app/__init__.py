import os
from flask import Flask
from .extensions import db, login_manager, csrf  # csrfを追加


def create_app():
    # -----------------------
    # Flask アプリ作成
    # -----------------------
    app = Flask(__name__, instance_relative_config=True)

    # -----------------------
    # 秘密鍵（セッション用）
    # -----------------------
    app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

    # -----------------------
    # 設定
    # -----------------------
    # instance フォルダ内に SQLite を置く
    os.makedirs(app.instance_path, exist_ok=True)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"sqlite:///{os.path.join(app.instance_path, 'myapp.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.config["WTF_CSRF_TIME_LIMIT"] = None  # CSRFトークンの有効期限

    # -----------------------
    # Extensions 初期化
    # -----------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # auth_bp の login を指す

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
    # DB 初期化（必要に応じて）
    # -----------------------
    with app.app_context():
        db.create_all()

    return app
