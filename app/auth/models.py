import re
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db

# ← ここを修正！（プロジェクト直下の extensions.py からimport）


# ======================
# フォロー関係テーブル（中間テーブル）
# ======================
followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)


# ======================
# Userモデル
# ======================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(200), default="default.png")
    bio = db.Column(db.Text, default="")

    # OTP関連
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiration = db.Column(db.DateTime, nullable=True)

    # フォロー関係（自己参照リレーション）
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    # ======================
    # コンストラクタ
    # ======================
    def __init__(self, username, email, password, icon="default.png", bio=""):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("メールアドレスの形式が不正です。")
        self.username = username
        self.email = email
        self.set_password(password)
        self.icon = icon
        self.bio = bio

    # ======================
    # パスワード関連
    # ======================
    def set_password(self, password: str):
        """パスワードをハッシュ化して保存"""
        if len(password) < 8:
            raise ValueError("パスワードは8文字以上にしてください。")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """ハッシュ化されたパスワードを検証"""
        return check_password_hash(self.password_hash, password)

    # ======================
    # OTP関連
    # ======================
    def set_otp(self) -> str:
        """ワンタイムパスワードを生成し、有効期限を設定"""
        code = f"{random.randint(100000, 999999)}"
        self.otp_code = code
        self.otp_expiration = datetime.utcnow() + timedelta(minutes=10)
        return code

    def verify_otp(self, code: str) -> bool:
        """OTPを検証"""
        return (
            self.otp_code == code
            and self.otp_expiration
            and datetime.utcnow() < self.otp_expiration
        )

    def clear_otp(self):
        """OTP情報をリセット"""
        self.otp_code = None
        self.otp_expiration = None

    # ======================
    # フォロー関連
    # ======================
    def follow(self, user):
        """指定ユーザーをフォロー"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """指定ユーザーのフォロー解除"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user) -> bool:
        """指定ユーザーをフォローしているか"""
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_count(self) -> int:
        """自分がフォローしている人数"""
        return self.followed.count()

    def followers_count(self) -> int:
        """自分をフォローしている人数"""
        return self.followers.count()

    def __repr__(self):
        return f"<User {self.username}>"
