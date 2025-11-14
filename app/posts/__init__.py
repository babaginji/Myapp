# posts/__init__.py
# 共通の db インスタンスを使用
from app.auth.models import db

# posts/models.py にすべてのモデルが統合されているため、
# 個別の user/post/like/comment モジュールはインポート不要。
from .models import Post, Like, Comment
