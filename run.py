import sys
import os

# myapp フォルダを Python のパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db  # db は extensions からインポート

app = create_app()

# アプリコンテキスト内でテーブルを作成（初回のみ）
with app.app_context():
    db.create_all()

# Render ではポートとホストを環境変数から取得
port = int(os.environ.get("PORT", 5000))
host = "0.0.0.0"

if __name__ == "__main__":
    app.run(debug=True, host=host, port=port)
