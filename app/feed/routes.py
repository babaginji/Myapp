from flask import Blueprint, render_template

feed_bp = Blueprint(
    "feed", __name__, template_folder="templates", static_folder="static"
)


@feed_bp.route("/")
def feed_home():
    return render_template("feed/feed.html")
