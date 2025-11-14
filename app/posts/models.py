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

    def __repr__(self):
        return f"<Post {self.id} by User {self.user_id}: {self.title}>"


# ----------------------
# Likeモデル
# ----------------------
class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
    post = db.relationship("Post", backref=db.backref("comments", lazy="dynamic"))

    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Post {self.post_id}>"
