from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.posts.models import Post, Like, Comment, Repost

feed_bp = Blueprint("feed", __name__, template_folder="templates", url_prefix="/feed")


@feed_bp.route("/")
def feed_home():
    # 投稿を作成日順に取得
    posts = Post.query.order_by(Post.created_at.desc()).all()

    # 各投稿にコメントリストを追加
    for post in posts:
        post.ordered_comments = post.comments.order_by(Comment.created_at.asc()).all()

    return render_template("feed/feed.html", posts=posts)


# ❤️ いいね
@feed_bp.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        count = post.likes.count()
        return jsonify({"liked": False, "count": count})

    new_like = Like(user_id=current_user.id, post_id=post.id)
    db.session.add(new_like)
    db.session.commit()
    count = post.likes.count()
    return jsonify({"liked": True, "count": count})


# 💬 コメント（Ajax用部分テンプレート返却）
@feed_bp.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment(post_id):
    content = request.json.get("content", "")
    if not content:
        return jsonify({"error": "empty"}), 400

    # コメントを追加
    new_comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
    )
    db.session.add(new_comment)
    db.session.commit()

    # 最新コメントを取得
    post = Post.query.get_or_404(post_id)
    ordered_comments = post.comments.order_by(Comment.created_at.asc()).all()

    # 部分テンプレートでレンダリング
    comments_html = render_template("feed/_comments.html", comments=ordered_comments)

    return jsonify({"ok": True, "comments_html": comments_html})


# 🔁 転送
@feed_bp.route("/repost/<int:post_id>", methods=["POST"])
@login_required
def repost(post_id):
    new_rp = Repost(
        user_id=current_user.id,
        post_id=post_id,
    )
    db.session.add(new_rp)
    db.session.commit()
    return jsonify({"ok": True})
