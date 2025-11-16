import os
import logging
from flask import Flask
from .extensions import db, login_manager, csrf


def create_app():
    # Flask アプリ作成
    app = Flask(__name__, instance_relative_config=True)

    # -----------------------
    # ログ設定
    # -----------------------
    logging.basicConfig(level=logging.DEBUG)  # DEBUG レベルで全部出す
    logger = logging.getLogger(__name__)
    logger.debug("Creating Flask app...")

    # -----------------------
    # 秘密鍵（セッション用）
    # -----------------------
    app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
    logger.debug(f"SECRET_KEY set: {app.secret_key[:8]}...")  # 一部だけ表示

    # -----------------------
    # 設定
    # -----------------------
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "myapp.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.config["WTF_CSRF_TIME_LIMIT"] = None

    # -----------------------
    # Extensions 初期化
    # -----------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    csrf.init_app(app)
    logger.debug("Extensions initialized.")

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
    logger.debug("Blueprints registered.")

    # -----------------------
    # DB 初期化（初回のみ）
    # -----------------------
    with app.app_context():
        try:
            db.create_all()
            logger.debug("Database tables created or already exist.")
        except Exception as e:
            logger.exception("Error creating database tables: %s", e)

    return app
