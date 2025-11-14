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
    icon_url = url_for(
        "auth.static", filename=f"icons/{getattr(current_user, 'icon', 'default.png')}"
    )
    return render_template("auth/profile.html", user=current_user, icon_url=icon_url)


# ----------------------
# プロフィール編集
# ----------------------
@auth_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = getattr(form, "bio", getattr(current_user, "bio", ""))

        # アイコンアップロード
        if form.icon.data:
            upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(form.icon.data.filename)
            filepath = os.path.join(upload_folder, filename)
            form.icon.data.save(filepath)
            current_user.icon = filename

        db.session.commit()
        flash("プロフィールを更新しました！", "success")
        return redirect(url_for("auth.profile"))

    # 初期値
    form.username.data = current_user.username
    form.bio.data = getattr(current_user, "bio", "")

    return render_template("auth/edit_profile.html", form=form)


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
