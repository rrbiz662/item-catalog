#!/usr/bin/env python2
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, exc
from db_model import Base, Category, Item, User
import json
import requests
import os
import datetime
import random
import string
import httplib2
import pdb


app = Flask(__name__)
auth = HTTPBasicAuth()
APPLICATION_NAME = "Catalog Application"

# Connect to database and create database session.
engine = create_engine("sqlite:///catalog.db")
Base.metadata.bind = engine
dbSession = sessionmaker(bind=engine)
session = dbSession()


# Login/Logout methods.
@app.route("/login/")
def show_login():
    # Create anti-forgery state token.
    state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

    login_session["state"] = state
    return render_template("login.html", STATE=state)


@app.route("/connect/", methods=["POST"])
def local_connect():
    # Get form data.
    if "user" in request.form:
        user_name = request.form["user"]
    if "password" in request.form:
        password = request.form["password"]

    # Attempt to get user. 
    try:
        user = session.query(User).filter_by(name=user_name).one()
    except exc.NoResultFound:
        user = None

    # Verify user and password. 
    if user is not None and user.verify_password(password):
        login_session["provider"] = "local"
        login_session["username"] = user.name
        login_session["email"] = user.email
        login_session["picture"] = user.picture
        login_session["user_id"] = user.id
        login_session["access_token"] = user.generate_auth_token(login_session["state"])

        return redirect(url_for("show_categories"))
    elif user is not None and not user.verify_password(password):
        flash("Invalid password.")
        return render_template("login.html")
    else:
        flash("User does not exist. Please create account.")
        return redirect(url_for("create_local_user"))


@app.route("/disconnect/")
def disconnect():
    if "provider" in login_session:
        if login_session["provider"] == "facebook":
            fbdisconnect()
            del login_session["facebook_id"]

        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]
        del login_session["provider"]
        del login_session["access_token"]

        flash("User has been logged out.")

        return redirect(url_for("show_categories"))
    else:
        return redirect(url_for("show_categories"))


@app.route("/fbconnect/", methods=["POST"])
def fbconnect():
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    access_token = request.data
    
    # Exchange user access token for long-lived server token.
    app_id = json.loads(open("fb_client_secrets.json", "r").read())[
        "web"]["app_id"]
    app_secret = json.loads(
        open("fb_client_secrets.json", "r").read())["web"]["app_secret"]
    url = "https://graph.facebook.com/v2.12/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s" % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, "GET")[1]
    """
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    """
    token = result.split(",")[0].split(":")[1].replace("\"", "")

    # Use token to get user info from API.
    url = "https://graph.facebook.com/v2.12/me?access_token=%s&fields=name,id,email" % token
    h = httplib2.Http()
    result = h.request(url, "GET")[1]
    data = json.loads(result)
    login_session["provider"] = "facebook"
    login_session["username"] = data["name"]
    login_session["email"] = data["email"]
    login_session["facebook_id"] = data["id"]

    # The token must be stored in the login_session in order to properly logout.
    login_session["access_token"] = token

    # Get user picture
    url = "https://graph.facebook.com/v2.12/me/picture?access_token=%s&redirect=0&height=200&width=200" % token
    h = httplib2.Http()
    result = h.request(url, "GET")[1]
    data = json.loads(result)
    
    login_session["picture"] = data["data"]["url"]

    # Check if user exists.
    user_id = get_user_id(login_session["email"])
    if not user_id:
        user_id = create_user()
    login_session["user_id"] = user_id

    return redirect(url_for("show_categories"))


@app.route("/fbdisconnect/")
def fbdisconnect():
    facebook_id = login_session["facebook_id"]
    # The access token must me included to successfully logout
    access_token = login_session["access_token"]
    url = "https://graph.facebook.com/%s/permissions?access_token=%s" % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, "DELETE")[1]


# JSON APIs to view catalog info.
@app.route("/catalog/<string:category_name>/<string:item_name>/JSON/")
def item_JSON(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    return jsonify(item=item.serialize)


@app.route("/catalog/<string:category_name>/JSON/")
def category_items_JSON(category_name):
    category = session.query(Category).filter_by(category=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return jsonify(items=[i.serialize for i in items])


@app.route("/catalog/JSON/")
def categories_JSON():
    categories = session.query(Category).all()
    return jsonify(categories=[cat.serialize for cat in categories])
    

# CRUD methods. 
@app.route("/")
@app.route("/catalog/")
def show_categories():
    categories = session.query(Category).order_by(asc(Category.category)).all()
    return render_template("categories.html", categories=categories)


@app.route("/catalog/category/new", methods=["GET", "POST"])
def create_category():
    if "user_id" not in login_session:
        return redirect(url_for("show_login"))

    if not is_valid_token(login_session["provider"]):
        return redirect(url_for("disconnect"))

    if request.method == "POST":
        if "create" in request.form:
            new_category = Category(category=request.form["category"], user_id=login_session["user_id"])
            session.add(new_category)
            session.commit()

        return redirect(url_for("show_categories"))
    else:
        return render_template("new_category.html")


@app.route("/catalog/<string:category_name>/edit/", methods=["GET", "POST"])
def edit_category(category_name):
    if "user_id" not in login_session:
        return redirect(url_for("show_login"))

    if not is_valid_token(login_session["provider"]):
        return redirect(url_for("disconnect"))

    category = session.query(Category).filter_by(category=category_name).one()
    if request.method == "POST":
        if "update" in request.form:
            category.category = request.form["category"]
            session.add(category)
            session.commit()       

        return redirect(url_for("show_categories"))
    else:
        if login_session["user_id"] != category.user_id:
            flash("Insufficent privileges.")
            return redirect(url_for("show_categories"))
        else:
            return render_template("edit_category.html", category=category)


@app.route("/catalog/<string:category_name>/delete/", methods=["GET", "POST"])
def delete_category(category_name):
    if "user_id" not in login_session:
        return redirect(url_for("show_login"))

    if not is_valid_token(login_session["provider"]):
        return redirect(url_for("disconnect"))

    category = session.query(Category).filter_by(category=category_name).one()
    if request.method == "POST":
        if "delete" in request.form:
            session.delete(category)
            session.commit()

        return redirect(url_for("show_categories"))
    else:
        if login_session["user_id"] != category.user_id:
            flash("Insufficent privileges.")
            return redirect(url_for("show_categories"))
        else:
            return render_template("delete_category.html", category=category)


@app.route("/catalog/<string:category_name>/")
def show_items(category_name):
    category = session.query(Category).filter_by(category=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).order_by(asc(Item.name)).all()
    return render_template("items.html", items=items, category=category)


@app.route("/catalog/<string:category_name>/<string:item_name>/")
def show_item(category_name, item_name):
    category= session.query(Category).filter_by(category=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()
    return render_template("item.html", category=category, item=item)


@app.route("/catalog/<string:category_name>/new/", methods=["GET", "POST"])
def create_item(category_name):
    if "user_id" not in login_session:
        return redirect(url_for("show_login"))

    if not is_valid_token(login_session["provider"]):
        return redirect(url_for("disconnect"))

    category = session.query(Category).filter_by(category=category_name).one()
    categories = session.query(Category).all()
    if request.method == "POST":
        if "create" in request.form:
            name = request.form["name"]            
            description = request.form["description"]
            category = session.query(Category).filter_by(category=request.form["categories"]).one()
            category_id = category.id

            newItem = Item(name=name, description=description, category_id=category_id, user_id=login_session["user_id"])
            session.add(newItem)
            session.commit()

        return redirect(url_for("show_items", category_name=category_name))
    else:
        return render_template("new_item.html", category_name=category_name, categories=categories)


@app.route("/catalog/<string:category_name>/<string:item_name>/edit/", methods=["GET", "POST"])
def edit_item(category_name, item_name):
    if "user_id" not in login_session:
        return redirect(url_for("show_login"))

    if not is_valid_token(login_session["provider"]):
        return redirect(url_for("disconnect"))

    category = session.query(Category).filter_by(category=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    if request.method == "POST":
        if "update" in request.form:
            item.name = request.form["name"]
            item.description = request.form["description"]
            category = session.query(Category).filter_by(category=request.form["categories"]).one()
            item.category_id = category.id
            session.add(item)
            session.commit()

        return redirect(url_for("show_items", category_name=category_name))
    else:
        if login_session["user_id"] != item.user_id:
            flash("Insufficent privileges.")
            return redirect(url_for("show_items", category_name=category_name))
        else:
            return render_template("edit_item.html", item=item, categories=categories, category=category)


@app.route("/catalog/<string:category_name>/<string:item_name>/delete/", methods=["GET", "POST"])
def delete_item(category_name, item_name):
    if "user_id" not in login_session:
        return redirect(url_for("show_login"))

    if not is_valid_token(login_session["provider"]):
        return redirect(url_for("disconnect"))

    category = session.query(Category).filter_by(category=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()
    if request.method == "POST":
        if "delete" in request.form:
            session.delete(item)
            session.commit()

        return redirect(url_for("show_items", category_name=category_name))
    else:
        if login_session["user_id"] != item.user_id:
            flash("Insufficent privileges.")
            return redirect(url_for("show_items", category_name=category_name))
        else:
            return render_template("delete_item.html", item=item, category=category)


@app.route("/catalog/user/new/", methods=["GET", "POST"])
def create_local_user():    
    if request.method == "POST":
        if "create" in request.form:
            login_session["provider"] = "local"
            login_session["username"] = request.form["username"]
            login_session["email"] = request.form["email"]
            login_session["picture"] = None
            user_id = create_user(request.form["password"])
            user = session.query(User).filter_by(id=user_id).one()
            login_session["user_id"] = user_id
            login_session["access_token"] = user.generate_auth_token(login_session["state"])

        return redirect(url_for("show_categories"))
    else:
        return render_template("new_user.html")


# Helper methods. 
def create_user(password=None):
    newUser = User(name=login_session["username"],
        email=login_session["email"], picture=login_session["picture"])

    if login_session["provider"] == "local" and password is not None:
        newUser.hash_password(password)

    session.add(newUser)
    session.commit()
    return newUser.id


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.template_filter("datetime_formatter")
def datetime_formatter(date, format="%b %d %Y"):
    return date.strftime(format)


def is_valid_token(provider):
    valid_token = True

    # Check local token validity.
    if provider == "local":
        user_id = User.verify_auth_token(login_session["access_token"], login_session["state"])
        if user_id is None:
            valid_token = False

    # Check facebook token validity.
    if provider == "facebook":
        url = "https://graph.facebook.com/v2.12/me?access_token=%s" % login_session["access_token"]
        h = httplib2.Http()
        result = h.request(url, "GET")[1]
        data = json.loads(result)

        if "type" in data and data["type"] == "OAuthException":
            if "code" in data and data["code"] == 190:
                valid_token = False

    return valid_token


if __name__ == "__main__":
    # Running module as a program.
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host="0.0.0.0", port=5000)