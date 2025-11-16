from datetime import datetime
from app.auth.models import db, User

# ----------------------
# Postモデル
# ----------------------
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship("User", backref=db.backref("posts", lazy="dynamic"))

    # ここは名前かぶりしないようにbackrefを変更
    likes = db.relationship(
        "Like", backref="post_ref", lazy="dynamic", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", backref="post_ref", lazy="dynamic", cascade="all, delete-orphan"
    )
    reposts = db.relationship(
        "Repost", backref="post_ref", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}: {self.title}>"

    def is_liked_by(self, user):
        """ユーザーがこの投稿にいいねしているか"""
        if not user.is_authenticated:
            return False
        return (
            Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None
        )


# ----------------------
# Likeモデル
# ----------------------
class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("likes", lazy="dynamic"))

    def __repr__(self):
        return f"<Like {self.id} by User {self.user_id} on Post {self.post_id}>"


# ----------------------
# Commentモデル
# ----------------------
class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship("User", backref=db.backref("comments", lazy="dynamic"))
    # backrefをPost.commentsと被らない名前に変更
    post = db.relationship(
        "Post", backref=db.backref("comments_from_comment", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Post {self.post_id}>"


# ----------------------
# Repostモデル（転送）
# ----------------------
class Repost(db.Model):
    __tablename__ = "reposts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("reposts", lazy="dynamic"))
    post = db.relationship(
        "Post", backref=db.backref("reposts_from_repost", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Repost {self.id} by User {self.user_id} on Post {self.post_id}>"
