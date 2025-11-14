# app/invest_clock/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date

invest_clock_bp = Blueprint("invest_clock", __name__, template_folder="templates")

# ---------------------------
# 定数
# ---------------------------
TARGET_AGE = 84
ANNUAL_INTEREST = 0.07
CURRENT_HOURLY_VALUE = 2600  # JS と同じ値に合わせる

# ---------------------------
# 複利計算（秒単位）
# ---------------------------
def calculate_future_value_seconds(birth_date):
    today = date.today()

    # 年齢計算（誕生日が来ていない場合は1歳引く）
    age_years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age_years -= 1

    # 残り年数＋日数
    remaining_years = TARGET_AGE - age_years - 1
    remaining_days = 365.25 - (
        (today - birth_date.replace(year=today.year)).days % 365.25
    )

    # 1秒あたりの人的資本（現在値を秒換算）
    per_second = CURRENT_HOURLY_VALUE / 3600

    # 年利複利
    value_after_years = per_second * ((1 + ANNUAL_INTEREST) ** remaining_years)

    # 日利換算
    daily_rate = (1 + ANNUAL_INTEREST) ** (1 / 365.25) - 1
    value_after_days = value_after_years * ((1 + daily_rate) ** remaining_days)

    return value_after_days


# ---------------------------
# ルート
# ---------------------------
@invest_clock_bp.route("/", methods=["GET", "POST"])
def clock_home():
    # デフォルト値
    birthday_str = request.form.get("birthday")
    theme = request.form.get("theme", "light")

    if birthday_str:
        try:
            birth_date = date.fromisoformat(birthday_str)
        except ValueError:
            birth_date = None
    else:
        birth_date = None

    # 計算
    if birth_date:
        fv_per_second = calculate_future_value_seconds(birth_date)
        age = date.today().year - birth_date.year
        if (date.today().month, date.today().day) < (birth_date.month, birth_date.day):
            age -= 1
    else:
        fv_per_second = CURRENT_HOURLY_VALUE / 3600
        age = 30  # デフォルト年齢

    fv_per_hour = fv_per_second * 3600

    return render_template(
        "invest_clock/clock.html",
        default_age=age,
        future_value=round(fv_per_hour, 2),
        theme=theme,
    )
