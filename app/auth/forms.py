# auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[DataRequired(message="ユーザー名を入力してください"), Length(min=2, max=20)],
    )
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスを入力してください"),
            Email(message="有効なメールアドレスを入力してください"),
        ],
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(message="パスワードを入力してください"),
            Length(min=8, message="パスワードは8文字以上です"),
        ],
    )
    confirm = PasswordField(
        "パスワード確認",
        validators=[
            DataRequired(message="パスワード確認を入力してください"),
            EqualTo("password", message="パスワードが一致しません"),
        ],
    )
    submit = SubmitField("登録")


class LoginForm(FlaskForm):
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")


class EditProfileForm(FlaskForm):
    username = StringField("ユーザー名", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    bio = StringField("自己紹介", validators=[Length(max=200)])
    submit = SubmitField("更新")
