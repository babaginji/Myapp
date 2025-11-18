import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.models import User
from app.auth.forms import RegisterForm, LoginForm, EditProfileForm
from app.extensions import db, login_manager

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", static_folder="static")

# ----------------------
# Flask-Login user_loader
# ----------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------------
# 登録
# ----------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("このメールアドレスはすでに登録されています。", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("登録完了！ログインしてください。", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


# ----------------------
# ログイン
# ----------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("ログイン成功！", "success")
            return redirect(url_for("feed.feed_home"))
        flash("メールアドレスまたはパスワードが違います。", "danger")

    return render_template("auth/login.html", form=form)


# ----------------------
# ログアウト
# ----------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました。", "info")
    return redirect(url_for("auth.login"))


# ----------------------
# プロフィール表示
# ----------------------
@auth_bp.route("/profile")
@login_required
def profile():
    # user_id がなければ current_user
    user_id = request.args.get("user_id", current_user.id)
    user = User.query.get(user_id)
    if not user:
        flash("ユーザーが存在しません。", "danger")
        return redirect(url_for("feed.feed_home"))

    # キャッシュ回避のためにクエリパラメータを追加
    icon_url = (
        url_for(
            "auth.static",
            filename=f"icons/{getattr(user, 'icon', 'default.png')}",
        )
        + f"?v={user.id}{getattr(user, 'icon', '')}"
    )

    return render_template("auth/profile.html", user=user, icon_url=icon_url)


# ----------------------
# プロフィール編集
# ----------------------
@auth_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        # ユーザー名・自己紹介更新
        current_user.username = form.username.data
        current_user.bio = getattr(form, "bio", getattr(current_user, "bio", ""))

        # アップロードされたアイコン画像を処理
        cropped_icon = request.files.get("cropped_icon")
        if cropped_icon and cropped_icon.filename:
            # 安全なファイル名と拡張子取得
            filename_secure = secure_filename(cropped_icon.filename)
            _, ext = os.path.splitext(filename_secure)
            ext = ext.lower() if ext else ".png"

            # 保存先フォルダ
            upload_folder = os.path.join(current_app.root_path, "static", "icons")
            os.makedirs(upload_folder, exist_ok=True)

            # ファイル名は userID + 拡張子
            filename = f"{current_user.id}{ext}"
            filepath = os.path.join(upload_folder, filename)

            # 保存
            cropped_icon.save(filepath)
            current_user.icon = filename

        # DB保存
        db.session.commit()
        flash("プロフィールを更新しました！", "success")
        return redirect(url_for("auth.profile", user_id=current_user.id))

    # GETの場合、フォーム初期値設定
    form.username.data = current_user.username
    form.bio.data = getattr(current_user, "bio", "")

    return render_template("auth/edit_profile.html", form=form, user=current_user)


# ----------------------
# パスワードリセット（簡易版）
# ----------------------
@auth_bp.route("/reset", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            flash("メールアドレスを入力してください", "danger")
            return redirect(url_for("auth.reset_request"))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("該当ユーザーなし", "danger")
            return redirect(url_for("auth.reset_request"))

        flash(f"{email} にリセットリンクを送信しました（デモ）", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_request.html")
