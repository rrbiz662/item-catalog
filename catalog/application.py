#!/usr/bin/env python
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_model import Base, Category, Item, User
import json
import requests
import os
import datetime

app = Flask(__name__)

APPLICATION_NAME = "Catalog Application"

# Connect to database and create database session.
engine = create_engine("sqlite:///catalog.db")
Base.metadata.bind = engine
dbSession = sessionmaker(bind=engine)
session = dbSession()


# JSON APIs to view catalog info.
@app.route("/catalog/<string:cat>/<string:item_name>/JSON/")
def item_JSON(cat, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    return jsonify(item=item.serialize)


@app.route("/catalog/<string:cat>/JSON/")
def category_items_JSON(cat):
    category = session.query(Category).filter_by(category=cat).one()
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
    if request.method == "POST":
        if "create" in request.form:
            new_category = Category(category=request.form["category"], user_id="1")
            session.add(new_category)
            session.commit()
        return redirect(url_for("show_categories"))
    else:
        return render_template("new_category.html")


@app.route("/catalog/<string:cat>/edit/", methods=["GET", "POST"])
def edit_category(cat):
    category = session.query(Category).filter_by(category=cat).one()
    if request.method == "POST":
        if "update" in request.form and "category" in request.form:
            category.category = request.form["category"]
            session.add(category)
            session.commit()       

        return redirect(url_for("show_categories"))
    else:
        return render_template("edit_category.html", category=category)


@app.route("/catalog/<string:cat>/delete/", methods=["GET", "POST"])
def delete_category(cat):
    category = session.query(Category).filter_by(category=cat).one()
    if request.method == "POST":
        if "delete" in request.form:
            session.delete(category)
            session.commit()

        return redirect(url_for("show_categories"))
    else:
        return render_template("delete_category.html", category=category)


@app.route("/catalog/<string:cat>/")
def show_items(cat):
    category = session.query(Category).filter_by(category=cat).one()
    items = session.query(Item).filter_by(category_id=category.id).order_by(asc(Item.name)).all()
    return render_template("items.html", items=items, category=category)


@app.route("/catalog/<string:cat>/<string:item_name>/")
def show_item(cat, item_name):
    category= session.query(Category).filter_by(category=cat).one()
    item = session.query(Item).filter_by(name=item_name).one()
    return render_template("item.html", category=category, item=item)


@app.route("/catalog/<string:cat>/new/", methods=["GET", "POST"])
def create_item(cat):
    category = session.query(Category).filter_by(category=cat).one()
    categories = session.query(Category).all()
    if request.method == "POST":
        if "create" in request.form:
            if "name" in request.form:
                name = request.form["name"]            
            if "description" in request.form:
                description = request.form["description"]
            if "categories" in request.form:
                category = session.query(Category).filter_by(category=request.form["categories"]).one()
                category_id = category.id

            newItem = Item(name=name, description=description, category_id=category_id, user_id="1")
            session.add(newItem)
            session.commit()

        return redirect(url_for("show_items", cat=cat))
    else:
        return render_template("new_item.html", category_id=category.id, categories=categories)


@app.route("/catalog/<string:cat>/<string:item_name>/edit/", methods=["GET", "POST"])
def edit_item(cat, item_name):
    category = session.query(Category).filter_by(category=cat).one()
    item = session.query(Item).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    if request.method == "POST":
        if "update" in request.form:
            if "name" in request.form:
                item.name = request.form["name"]
            if "description" in request.form:
                item.description = request.form["description"]
            if "categories" in request.form:
                category = session.query(Category).filter_by(category=request.form["categories"]).one()
                item.category_id = category.id
            session.add(item)
            session.commit()

        return redirect(url_for("show_items", cat=cat))
    else:
        return render_template("edit_item.html", item=item, categories=categories, category=category)


@app.route("/catalog/<string:cat>/<string:item_name>/delete/", methods=["GET", "POST"])
def delete_item(cat, item_name):
    category = session.query(Category).filter_by(category=cat).one()
    item = session.query(Item).filter_by(name=item_name).one()
    if request.method == "POST":
        if "delete" in request.form:
            session.delete(item)
            session.commit()

        return redirect(url_for("show_items", cat=cat))
    else:
        return render_template("delete_item.html", item=item, category=category)


if __name__ == "__main__":
    # Running module as a program.
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host="0.0.0.0", port=5000)