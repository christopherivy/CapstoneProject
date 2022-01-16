import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import json

from forms import UserAddForm, LoginForm, SearchForm
from model import db, connect_db, User

CURR_USER_KEY = "curr_user"
API_KEY = "59487502"  # This key belongs to Christopher Ivy. Please get your own.
API_BASE_URL = "https://imdb-api.com/API/AdvancedSearch/k_ybkbttjb"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///cs_movies"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


# this is the home page aka (index.html)
@app.route("/", methods=["GET", "POST"])
def home_page():
    form = SearchForm()

    # when the user clicks search button
    if form.validate_on_submit():
        year = request.args(["year"])
        flash(year)
    #     res = request.get(f"{API_BASE_URL}", params={"release_date": year})
    #     print(res)
    #     data = res.json()
    # return render_template("index.html", data)
    # grab vals from form
    # hit API and return list of items

    return render_template("index.html", form=form)


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# handle user signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    #  create user form
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", "danger")
            return render_template("signup.html", form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template("signup.html", form=form)


# handle user login
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", "success")
    return redirect("/login")


@app.route("/search", methods=["GET", "POST"])
def search():
    """Handles search button"""

    res = request.get(f"{API_BASE_URL}", params={"title": "terminator"})
    print(res)
    data = res.json()
    return render_template("index.html", data)
