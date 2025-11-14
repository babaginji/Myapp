from flask import Blueprint, render_template

from app.posts.models import Post

# Post モデルを import
from flask_login import current_user  # 投稿フォーム表示用に必要なら

feed_bp = Blueprint("feed", __name__, template_folder="templates")


@feed_bp.route("/")
def feed_home():
    # 投稿を新しい順に取得
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("feed/feed.html", posts=posts, current_user=current_user)
