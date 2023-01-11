from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models.member import Member
from flask_app.models.recipe import Recipe
from flask import flash

@app.route("/recipes/home")
def recipes_home():
    if "member_id" not in session:
        flash("You must be logged in to access the dashboard.", "Login")
        return redirect("/")
    
    member = Member.get_member_id(session["member_id"])
    recipes = Recipe.get_all()

    return render_template("home.html", member=member, recipes=recipes)


@app.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    member = Member.get_member_id(session["member_id"])
    recipe = Recipe.get_by_id(recipe_id)
    return render_template("recipe_detail.html", member=member, recipe=recipe)

@app.route("/recipes/create")
def recipe_create_page():
    return render_template("create_recipe.html")

@app.route("/recipes/edit/<int:recipe_id>")
def recipe_edit_page(recipe_id):
    recipe = Recipe.get_by_id(recipe_id)
    return render_template("edit_recipe.html", recipe=recipe)

@app.route("/recipes", methods =["POST"])
def create_recipe():
        valid_recipe = Recipe.create_valid_recipe(request.form)
        if valid_recipe:
            return redirect(f'/recipes/{valid_recipe.id}')
        return redirect(f'/recipes/create')

@app.route("/recipes/<int:recipe_id>", methods=["POST"])
def update_recipe(recipe_id):
    valid_recipe = Recipe.update_recipe(request.form, session["member_id"])

    if not valid_recipe:
        return redirect(f"/recipes/edit/{recipe_id}")
    return redirect(f"/recipes/edit/{recipe_id}")

@app.route("/recipes/delete/<int:recipe_id>")
def delete_by_id(recipe_id):
    Recipe.delete_recipe_by_id(recipe_id)
    return redirect("/recipes/home")
