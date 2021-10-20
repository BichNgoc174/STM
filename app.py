from typing import NoReturn
from flask import Blueprint, render_template 
from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from flask import Flask 
from werkzeug.security import generate_password_hash, check_password_hash
#############################################
from pymongo import MongoClient
import pymongo
import os
import json

CONNECTION_STRING = "mongodb+srv://admin:admin@documentstm.t4ijg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
_limit_=20
global auth
db = SQLAlchemy()
main = Blueprint('main', __name__)
@main.route('/')
def home():
    myclient = MongoClient(CONNECTION_STRING)
    mydb = myclient["DocumentSTM"]
    
    mycol = mydb["category"]
    data_source =mydb["STM_DOC"]
    data=data_source.find().limit(5)
    category=mycol.find().limit(_limit_)
    return render_template('index.html',current_user=NoReturn,category=category,data=data)

@main.route('/viewPDF')
def viewPDF():
    path = 'static/pdf/'
    a = os.listdir(path)
    a.remove('.DS_Store')
    text = json.dumps(sorted(a))
    return render_template('viewPDF.html', contents = text)

@main.route('/index')
@login_required
def index():
    myclient = MongoClient(CONNECTION_STRING)
    mydb = myclient["DocumentSTM"]
    
    mycol = mydb["category"]
    data_source =mydb["STM_DOC"]
    data=data_source.find().limit(5)
    category=mycol.find().limit(_limit_)
   
    return render_template('index.html', name=current_user.name, category=category,data=data)
    
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# info login table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'thisismysecretkeydonotstealit'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth) # tạm bỏ
    app.register_blueprint(main)

    return app
app=create_app()

#https://www.youtube.com/watch?v=p_so34WgnyY fix lỗi flask

# first load the model and then start the server
if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=5000, debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)