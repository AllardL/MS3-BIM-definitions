import os
from flask import Flask, render_template, redirect, request, url_for, session 
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import pymongo
import re


#MONGO_URI = (os.environ.get('MONGO_URI'))

app = Flask(__name__)

#app.config["MONGO_URI"] = MONGO_URI
app.config["MONGO_URI"] = 'mongodb+srv://AllardDB:RxBuROru0OyhHyMC@gcpbelgium-fdk0n.gcp.mongodb.net/BIMDefinitions?retryWrites=true&w=majority'
app.config["SECRET_KEY"] = "allard85368"

mongo = PyMongo(app)

@app.route('/')
@app.route('/get_definitions')
def get_definitions():
        return render_template("definitions.html", definitions = mongo.db.definitions.find().sort("term",pymongo.ASCENDING),
                                languages=mongo.db.language.find().sort("name",pymongo.ASCENDING))



@app.route('/search_definition', methods=["POST"])
def search_definition():
    definitions = mongo.db.definitions
    form = request.form.to_dict()
    s_term = form["s_term"]
    s_language = form["s_language"]
    s_editor = form["s_editor"]

    filter = {}
    if s_term != "": filter['term'] = s_term
    if s_language != "": filter['language'] = s_language
    if s_editor != "": filter['user'] = s_editor
    definitions = mongo.db.definitions.find(filter).sort("term",pymongo.ASCENDING)
    result = definitions.count()

    return render_template("definitions.html", 
                            definitions = definitions,
                            languages=mongo.db.language.find().sort("name",pymongo.ASCENDING),
                            s_term = s_term, s_language = s_language, s_editor = s_editor, result = result)


@app.route('/add_definition')
def add_definition():
    return render_template('adddefinition.html',
                            languages=mongo.db.language.find().sort("name",pymongo.ASCENDING))



@app.route('/insert_definition', methods=['POST'])
def insert_definition():
    definitions = mongo.db.definitions
    form = request.form.to_dict()
    term = {
        'term':form["term"],
        'language':form["language"],
        'description': form["description"],
        'user': session['name'],        
        'uniqueKey':form["term"].lower().replace(" ","")+form["language"].lower()
    }
    definitions.insert_one(term)
    return redirect(url_for('get_definitions'))

@app.route('/edit_definition/<definition_id>')
def edit_definition(definition_id):
    the_definition = mongo.db.definitions.find_one({"_id": ObjectId(definition_id)})
    all_languages = mongo.db.language.find().sort("name",pymongo.ASCENDING)
    return render_template('editdefinition.html', definition=the_definition, languages = all_languages)

@app.route('/update_definition/<definition_id>', methods=["POST"])
def update_definition(definition_id):
    definitions = mongo.db.definitions
    form = request.form.to_dict()
    definitions.update( {'_id': ObjectId(definition_id)},
    {
        'term':form["term"],
        'language':form["language"],
        'description': form["description"],
        'user': session['name'],
        'uniqueKey':form["term"].lower().replace(" ","")+form["language"].lower()
    })
    return redirect(url_for('get_definitions'))


#USER RELATED 
@app.route('/user_signup')
def user_signup():
        return render_template("user/signup.html")

@app.route('/add_user', methods=['POST'])
def add_user():
    # define variables
    user = mongo.db.user
    form = request.form.to_dict()
    name = form["user_name"]
    email = form["user_email"].lower()
    userValidation = True
    pwValidation = True
    emailValidation = True
    userCount = user.find({'name': name }).count()
    emailCount = user.find({'email': email }).count()

    #user validation
    if  userCount > 0:
        userValidation = False

    #email validation
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    _email = pattern.match(form["user_email"])
    if email not in str(_email) or emailCount > 0:
        emailValidation = False

    #password validation
    if form["password"] != form["cpassword"]:
        pwValidation = False

    #add or refuse user
    Validation = [userValidation, emailValidation, pwValidation]
    if False in Validation:
        return render_template("user/signup.html",user_name = form["user_name"], user_email = form["user_email"], userValidation= userValidation, emailValidation = emailValidation, pwValidation = pwValidation)        
    else:
        pw = form["password"].encode('utf8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pw, salt)
        User = {
            'name':name,
            'email':email,
            'password': hashed_password,
        }
        session['name'] = name
        user.insert_one(User)
        return redirect(url_for('get_definitions'))

@app.route('/user_login')
def user_login():
    return render_template("user/login.html")


@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    form = request.form.to_dict()
    email = form["user_email"].lower()
    users = mongo.db.user
    userCount = users.find({'email': email }).count()
    if userCount > 0:
        user = users.find_one({"email": email})
        userpw = user['password']
        formpw = form['password'].encode('utf8')
        if bcrypt.checkpw(formpw, userpw):
            session['name'] = user['name']
            return redirect(url_for('get_definitions'))
        else:
            pwValidation = False
            return render_template("user/login.html", user_email = email, pwValidation = pwValidation)
    else:
        emailValidation = False
        return render_template("user/login.html", emailValidation = emailValidation)

@app.route('/user_edit')
def user_edit():
    users = mongo.db.user
    user = users.find_one({"name": session["name"]})
    email = user['email'].lower()        
    return render_template("user/edit.html", user_email = email, user_name = session['name'])

@app.route('/update_user', methods=["POST"])
def update_user():
    users = mongo.db.user
    form = request.form.to_dict()
    userValidation = True
    pwValidation = True
    emailValidation = True
    email = form["user_email"].lower()
    user = users.find_one({"name": session["name"]})
    userID = user['_id']
    userpw = user['password']
    formpw = form['oldPassword'].encode('utf8')

    #user validation
    name = form["user_name"]
    userCount = users.find({'name': name }).count()
    if  userCount > 0 and name != session["name"]:
        userValidation = False

    #password validation
    if bcrypt.checkpw(formpw, userpw):
        pwValidationOld = True
    else:
        pwValidationOld = False

    #new password validation
    if len(form['password']) > 0:
        if form["password"] != form["cpassword"]:
            pwValidation = False
        elif pwValidationOld == True and userValidation == True:
            pwValidation = True
            pw = form["password"].encode('utf8')
            salt = bcrypt.gensalt()
            userpw = bcrypt.hashpw(pw, salt)

    #add or refuse userupdate
    Validation = [userValidation, pwValidationOld, pwValidation]
    if False in Validation:
        return render_template("user/edit.html",user_name = form["user_name"], user_email = form["user_email"], userValidation= userValidation, pwValidationOld = pwValidationOld, pwValidation = pwValidation)        
    else:
        session['name']=name
        users.update( {'_id': ObjectId(userID)},
            {
                'name':name,
                'email': email,
                'password': userpw,
            })
    return redirect(url_for('get_definitions'))


@app.route('/logout')
def logout():
    session.pop('name')
    return redirect(url_for('get_definitions'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')), 
        debug=True)