from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app.models import member
import re

db = "recipe_share"
class Recipe:
    def __init__(self, recipe):
        self.id = recipe["id"]
        self.name = recipe["name"]
        self.description = recipe["description"]
        self.instructions = recipe["instructions"]
        self.date_cooked = recipe["date_cooked"]
        self.under_30 = recipe["under_30"]
        self.created_at = recipe["created_at"]
        self.updated_at = recipe["updated_at"]
        self.member = None

    @classmethod
    def create_valid_recipe(cls, recipe_dict):
        if not cls.is_valid(recipe_dict):
            return False

        query = "INSERT INTO recipes (name, description, instructions, date_cooked, under_30, member_id) VALUES (%(name)s, %(description)s, %(instructions)s, %(date_cooked)s, %(under_30)s, %(member_id)s);"
        recipe_id = connectToMySQL(db).query_db(query, recipe_dict)
        recipe = cls.get_by_id(recipe_id)
        return recipe

    @classmethod
    def get_by_id(cls, recipe_id):
        print(f"get recipe by id {recipe_id}")
        data = {"id": recipe_id}
        query = """SELECT recipes.id, recipes.created_at, recipes.updated_at, recipes.instructions, recipes.description, recipes.name, recipes.date_cooked, under_30, members.id as member_id, members.first_name, members.last_name, members.email, members.password, members.created_at as uc, members.updated_at as uu
        FROM recipes
        JOIN members on members.id = recipes.member_id
        WHERE recipes.id = %(id)s;"""

        result = connectToMySQL(db).query_db(query,data)
        print("result of query:")
        print(result)
        result = result[0]
        recipe = cls(result)
        
        recipe.member = member.Member(
                {
                    "id": result["member_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["uc"],
                    "updated_at": result["uu"]
                }
            )
            
        return recipe

    @classmethod
    def delete_recipe_by_id(cls, recipe_id):
        data = {"id": recipe_id}
        query = "DELETE from recipes WHERE id = %(id)s;"
        connectToMySQL(db).query_db(query, data)

        return recipe_id

    @classmethod
    def update_recipe(cls, recipe_dict, session_id):
        recipe = cls.get_by_id(recipe_dict["id"])
        if recipe.member.id != session_id:
            flash("You must be the author to update this recipe.")
            return False
        if not cls.is_valid(recipe_dict):
            return False
        query = "UPDATE recipes SET name = %(name)s, description = %(description)s, instructions = %(instructions)s, date_cooked=%(date_cooked)s, under_30 = %(under_30)s WHERE id = %(id)s;"
        result = connectToMySQL(db).query_db(query,recipe_dict)
        recipe = cls.get_by_id(recipe_dict["id"])

        return recipe


    @classmethod
    def get_all(cls):
        query = """SELECT 
                    recipes.id, recipes.created_at, recipes.updated_at, instructions, description, name, date_cooked, under_30,
                    members.id as member_id, first_name, last_name, email, password, members.created_at as uc, members.updated_at as uu
                    FROM recipes
                    JOIN members on members.id = recipes.member_id;"""
        recipe_data = connectToMySQL(db).query_db(query)
        recipes = []
        for recipe in recipe_data:
            print (recipe_data)
            recipe_obj = cls(recipe)
            recipe_obj.member = member.Member(
                {
                    "id": recipe["member_id"],
                    "first_name": recipe["first_name"],
                    "last_name": recipe["last_name"],
                    "email": recipe["email"],
                    "password": recipe["password"],
                    "created_at": recipe["uc"],
                    "updated_at": recipe["uu"],
                }
            )
            recipes.append(recipe_obj)

        return recipes


    @staticmethod
    def is_valid(recipe_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        print(recipe_dict)
        if len(recipe_dict["name"]) < 3:
            flash("Name " + flash_string)
            valid = False
        if len(recipe_dict["description"]) < 3:
            flash("Description " + flash_string)
            valid = False
        if len(recipe_dict["instructions"]) < 3:
            flash("Instructions " + flash_string)
            valid = False
        if len(recipe_dict["date_cooked"]) <= 0:
            flash("Date is required")
            valid = False
        if "under_30" not in recipe_dict:
            flash("Does your recipe take less than 30 min?")
            valid = False

        return valid