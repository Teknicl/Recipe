from flask import Flask, render_template, request, redirect, session
from flask_app import app
from flask_app.models.member import Member
from flask import flash

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    valid_member = Member.create_valid_member(request.form)
    print(valid_member)
    if not valid_member:
        return redirect("/")
    session["member_id"] = valid_member.id
    return redirect("/recipes/home")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/login',methods=['POST'])
def login():
    valid_member = Member.authenticated_member_by_input(request.form)
    if not valid_member:
        return redirect("/")
    session["member_id"] = valid_member.id
    return redirect("/recipes/home")