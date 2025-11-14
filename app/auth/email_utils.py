# auth/email_utils.py
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_otp_email(user, code):
    """
    ユーザー宛にパスワードリセット用のOTPメールを送信する。

    Parameters:
    - user: User オブジェクト（.email 属性が必要）
    - code: 送信するワンタイムコード
    """
    if not hasattr(user, "email") or not user.email:
        raise ValueError("ユーザーに有効なメールアドレスが設定されていません。")

    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "no-reply@example.com")
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        raise EnvironmentError("SENDGRID_API_KEY が設定されていません。")

    message = Mail(
        from_email=from_email,
        to_emails=user.email,
        subject="パスワードリセットコード",
        plain_text_content=f"あなたの確認コードは {code} です。",
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info(f"Email送信ステータス: {response.status_code}")
        return response.status_code
    except Exception as e:
        logger.error(f"Email送信中にエラー発生: {e}")
        raise
