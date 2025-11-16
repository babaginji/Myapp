import os
from flask import Flask
from .extensions import db, login_manager, csrf


def create_app():
    # Flask アプリ作成
    app = Flask(__name__, instance_relative_config=True)

    # -----------------------
    # 秘密鍵（セッション用）
    # -----------------------
    # 環境変数から取得。なければ開発用キーを使用
    app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

    # -----------------------
    # 設定
    # -----------------------
    # instance フォルダを作成（SQLite やアップロード先）
    os.makedirs(app.instance_path, exist_ok=True)

    # SQLite DB パス
    db_path = os.path.join(app.instance_path, "myapp.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # アップロード先
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # CSRF トークンの有効期限なし
    app.config["WTF_CSRF_TIME_LIMIT"] = None

    # -----------------------
    # Extensions 初期化
    # -----------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    csrf.init_app(app)

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
    # DB 初期化（初回のみ）
    # -----------------------
    with app.app_context():
        db.create_all()

    return app
