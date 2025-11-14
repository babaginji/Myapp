from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.extensions import db
from app.posts.models import Post, Like, Comment

post_bp = Blueprint("post", __name__, url_prefix="/")


@post_bp.route("/", methods=["GET"])
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("posts/index.html", posts=posts)


@post_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("タイトルと内容は必須です。", "danger")
            return redirect(url_for("post.create_post"))

        try:
            post = Post(title=title, content=content, user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("投稿を作成しました！", "success")
            return redirect(url_for("post.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"投稿作成中にエラーが発生しました: {e}", "danger")
            return redirect(url_for("post.create_post"))

    return render_template("posts/create_post.html")


@post_bp.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like(post_id):
    try:
        existing_like = Like.query.filter_by(
            user_id=current_user.id, post_id=post_id
        ).first()

        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()
            liked = False
        else:
            new_like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(new_like)
            db.session.commit()
            liked = True

        like_count = Like.query.filter_by(post_id=post_id).count()
        return jsonify({"liked": liked, "like_count": like_count})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@post_bp.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def comment(post_id):
    content = request.form.get("content", "").strip()
    if not content:
        return jsonify({"error": "コメントが空です"}), 400

    try:
        new_comment = Comment(user_id=current_user.id, post_id=post_id, content=content)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify(
            {
                "id": new_comment.id,
                "user": current_user.username,
                "content": new_comment.content,
                "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@post_bp.route("/<int:post_id>", methods=["GET"])
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = (
        Comment.query.filter_by(post_id=post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    like_count = Like.query.filter_by(post_id=post_id).count()
    liked_by_user = (
        Like.query.filter_by(
            post_id=post_id,
            user_id=current_user.get_id() if current_user.is_authenticated else None,
        ).first()
        is not None
    )

    return render_template(
        "posts/detail.html",
        post=post,
        comments=comments,
        like_count=like_count,
        liked_by_user=liked_by_user,
    )
