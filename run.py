import sys
import os

# myapp フォルダを Python のパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.auth.models import db  # ← db をインポートしてテーブル作成に使う

app = create_app()

# アプリコンテキスト内でテーブルを作成
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
