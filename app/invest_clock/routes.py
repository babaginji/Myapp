from flask import Blueprint, render_template

invest_clock_bp = Blueprint(
    "invest_clock", __name__, url_prefix="/clock", template_folder="templates"
)


TARGET_AGE = 84
ANNUAL_INTEREST = 0.07  # 7%


def calculate_future_value(age):
    years_to_go = TARGET_AGE - age
    return 1 * (1 + ANNUAL_INTEREST) ** years_to_go


@invest_clock_bp.route("/")
def clock_home():
    default_age = 30
    fv_per_second = calculate_future_value(default_age)
    fv_per_hour = fv_per_second * 3600  # 1時間あたり
    return render_template(
        "invest_clock/clock.html",
        default_age=default_age,
        future_value=round(fv_per_hour, 2),
    )
