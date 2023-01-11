from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app)

db = "recipe_share"
class Member:
    def __init__(self,member):
        self.id = member['id']
        self.first_name = member['first_name']
        self.last_name = member['last_name']
        self.email = member['email']
        self.password = member['password']
        self.created_at = member['created_at']
        self.updated_at = member['updated_at']

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def get_member_id(cls, member_id):
        data = {"id": member_id}
        query = "SELECT * FROM members WHERE id = %(id)s;"
        result = connectToMySQL(db).query_db(query, data)
        
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_member_email(cls,email):
        data = {
            "email": email
        }
        query = "SELECT * FROM members WHERE email = %(email)s;"
        result = connectToMySQL(db).query_db(query,data)

        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_all(cls):
        query = "SELECT * from members;"
        member_data = connectToMySQL(db).query_db(query)
        
        members = []
        for member in member_data:
            members.append(cls(member))
        return members

    @classmethod
    def create_valid_member(cls, member):
        if not cls.is_valid(member):
            return False

        pw_hash = bcrypt.generate_password_hash(member['password'])
        member = member.copy()
        member["password"] = pw_hash
        print("Member after adding pw: ", member)

        query = """
                INSERT into members (first_name, last_name, email, password)
                VALUES (%(fname)s, %(lname)s, %(email)s, %(password)s);"""

        new_member_id = connectToMySQL(db).query_db(query, member)
        new_member = cls.get_member_id(new_member_id)

        return new_member

    @classmethod
    def is_valid(cls, member):
        valid = True

        if len(member['fname']) <2:
            flash("First must be at least 2 characters.","Register")
            valid = False
        if len(member['lname']) <2:
            flash("Last must be at least 2 characters.","Register")
            valid = False
        if not EMAIL_REGEX.match(member['email']):
            flash("Invalid email address!","Register")
            valid = False
        if not member['password'] == member['confirm']:
            flash("Password does not match","Register")
            valid = False

        email_already_has_account = Member.get_member_email(member['email'])
        if email_already_has_account:
            flash("This account already exists.")
            valid = False
        return valid

    @classmethod
    def authenticated_member_by_input(cls, member_input):
        valid = True
        existing_member = cls.get_member_email(member_input["email"])
        password_valid = True

        if not existing_member:
            valid = False
        else:
            password_valid = bcrypt.check_password_hash(
            existing_member.password, member_input['password'])
            if not password_valid:
                valid = False
        if not valid:
            flash("Email and password does not match.", "Login")
            return False

        return existing_member