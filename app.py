import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import pymongo
import re

MONGO_URI = "mongodb+srv://AllardDB:" +(os.environ.get('MONGO_KEY')) +"@gcpbelgium-fdk0n.gcp.mongodb.net/BIMDefinitions?retryWrites=true&w=majority"
SECRET_KEY = (os.environ.get('SECRET_KEY'))
app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI
app.config["SECRET_KEY"] = SECRET_KEY

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_definitions')
def get_definitions():
    return render_template("definitions.html",
                           definitions=mongo.db.definitions.find().sort("term", pymongo.ASCENDING),
                           languages=mongo.db.language.find().sort("name", pymongo.ASCENDING))


@app.route('/search_definition', methods=["POST"])
def search_definition():
    definitions = mongo.db.definitions
    form = request.form.to_dict()
    s_term = form["s_term"]
    s_language = form["s_language"]
    s_editor = form["s_editor"]

    filter = {}
    if s_term != "":
        filter['term'] = {'$regex': s_term, '$options': '-i'}
    if s_language != "":
        filter['language'] = s_language
    if s_editor != "":
        filter['user'] = {'$regex': s_editor, '$options': '-i'}
    definitions = mongo.db.definitions.find(
        filter).sort("term", pymongo.ASCENDING)
    result = definitions.count()

    return render_template("definitions.html",
                           definitions=definitions,
                           languages=mongo.db.language.find().sort("name", pymongo.ASCENDING),
                           s_term=s_term,
                           s_language=s_language,
                           s_editor=s_editor,
                           result=result)


@app.route('/add_definition')
def add_definition():
    return render_template('adddefinition.html',
                           languages=mongo.db.language.find().sort("name", pymongo.ASCENDING))


@app.route('/insert_definition', methods=['POST'])
def insert_definition():
    definitions = mongo.db.definitions
    form = request.form.to_dict()
    term = {
        'term': form["term"],
        'language': form["language"],
        'description': form["description"],
        'user': session['name'],
        'uniqueKey': form["term"].lower().replace(" ", "")+form["language"].lower()
    }
    definitions.insert_one(term)
    return redirect(url_for('get_definitions'))


@app.route('/edit_definition/<definition_id>')
def edit_definition(definition_id):
    try:
        the_definition = mongo.db.definitions.find_one(
            {"_id": ObjectId(definition_id)})
    except bson.errors.InvalidId as e:
        flash('Cannot get that item!')
        print(f'Could not find the object ID in definitions, {e}')
        return redirect(url_for('get_definitions'))
    except Exception as e:
        flash('There was an error getting the item')
        print(f'There was an exception {e}')
        return redirect(url_for('get_definitions'))

    all_languages = mongo.db.language.find().sort("name", pymongo.ASCENDING)
    return render_template('editdefinition.html', definition=the_definition, languages=all_languages)


@app.route('/update_definition/<definition_id>', methods=["POST"])
def update_definition(definition_id):
    try:
        the_definition = mongo.db.definitions.find_one(
            {"_id": ObjectId(definition_id)})
    except bson.errors.InvalidId as e:
        flash('Cannot get that item!')
        print(f'Could not find the object ID in definitions, {e}')
        return redirect(url_for('get_definitions'))
    except Exception as e:
        flash('There was an error getting the item')
        print(f'There was an exception {e}')
        return redirect(url_for('get_definitions'))

    definitions = mongo.db.definitions
    form = request.form.to_dict()
    definitions.update({'_id': ObjectId(definition_id)},
    {
        'term': form["term"],
        'language': form["language"],
        'description': form["description"],
        'user': session['name'],
        'uniqueKey': form["term"].lower().replace(" ", "")+form["language"].lower()
    })
    return redirect(url_for('get_definitions'))


# USER RELATED
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
    user_validation = True
    pw_validation = True
    email_validation = True
    user_count = user.find({'name': name}).count()
    email_count = user.find({'email': email}).count()

    # user validation
    if user_count > 0:
        user_validation = False

    # email validation
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    _email = pattern.match(form["user_email"])
    if email not in str(_email) or email_count > 0:
        email_validation = False

    # password validation
    if form["password"] != form["cpassword"]:
        pw_validation = False

    # add or refuse user
    Validation = [user_validation, email_validation, pw_validation]
    if all(Validation):
        return render_template("user/signup.html", user_name=form["user_name"], user_email=form["user_email"], user_validation=user_validation, email_validation=email_validation, pw_validation=pw_validation)
    else:
        pw = form["password"].encode('utf8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pw, salt)
        User = {
            'name': name,
            'email': email,
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
    user_count = users.find({'email': email}).count()
    if user_count > 0:
        user = users.find_one({"email": email})
        userpw = user['password']
        formpw = form['password'].encode('utf8')
        if bcrypt.checkpw(formpw, userpw):
            session['name'] = user['name']
            return redirect(url_for('get_definitions'))
        else:
            pw_validation = False
            return render_template("user/login.html", user_email=email, pw_validation=pw_validation)
    else:
        email_validation = False
        return render_template("user/login.html", email_validation=email_validation)


@app.route('/user_edit')
def user_edit():
    users = mongo.db.user
    user = users.find_one({"name": session["name"]})
    email = user['email'].lower()
    return render_template("user/edit.html", user_email=email, user_name=session['name'])


@app.route('/update_user', methods=["POST"])
def update_user():
    users = mongo.db.user
    form = request.form.to_dict()
    user_validation = True
    pw_validation = True
    email_validation = True
    email = form["user_email"].lower()
    user = users.find_one({"name": session["name"]})
    userID = user['_id']
    userpw = user['password']
    formpw = form['oldPassword'].encode('utf8')

    # user validation
    name = form["user_name"]
    user_count = users.find({'name': name}).count()
    if user_count > 0 and name != session["name"]:
        user_validation = False

    # password validation
    if bcrypt.checkpw(formpw, userpw):
        pw_validation_old = True
    else:
        pw_validation_old = False

    # new password validation
    if len(form['password']) > 0:
        if form["password"] != form["cpassword"]:
            pw_validation = False
        elif pw_validation_old == True and user_validation == True:
            pw_validation = True
            pw = form["password"].encode('utf8')
            salt = bcrypt.gensalt()
            userpw = bcrypt.hashpw(pw, salt)

    # add or refuse userupdate
    validation = [user_validation, pw_validation_old, pw_validation]
    if not all(validation):
        return render_template("user/edit.html", user_name=form["user_name"], user_email=form["user_email"], user_validation=user_validation, pw_validation_old=pw_validation_old, pw_validation=pw_validation)
    else:
        session['name'] = name
        users.update({'_id': ObjectId(userID)},
        {
            'name': name,
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
            debug=False)
