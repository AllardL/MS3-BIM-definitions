import os
from flask import Flask, render_template, redirect, request, url_for 
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


#MONGO_URI = (os.environ.get('MONGO_URI'))

app = Flask(__name__)

#app.config["MONGO_URI"] = MONGO_URI
app.config["MONGO_URI"] = 'mongodb+srv://AllardDB:RxBuROru0OyhHyMC@gcpbelgium-fdk0n.gcp.mongodb.net/BIMDefinitions?retryWrites=true&w=majority'

mongo = PyMongo(app)

@app.route('/')
@app.route('/get_definitions')
def get_definitions():
        return render_template("definitions.html", definitions = mongo.db.definitions.find())

@app.route('/add_definition')
def add_definition():
    return render_template('adddefinition.html',
                            languages=mongo.db.language.find())

@app.route('/insert_definition', methods=['POST'])
def insert_definition():
    definitions = mongo.db.definitions
    form = request.form.to_dict()
    term = {
        'term':form["term"],
        'language':form["language"],
        'description': form["description"],
        'uniqueKey':form["term"].lower().replace(" ","")+form["language"].lower()
    }
    definitions.insert_one(term)
    return redirect(url_for('get_definitions'))

@app.route('/edit_definition/<definition_id>')
def edit_definition(definition_id):
    the_definition = mongo.db.definitions.find_one({"_id": ObjectId(definition_id)})
    all_languages = mongo.db.language.find()
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
        'uniqueKey':form["term"].lower().replace(" ","")+form["language"].lower()
    })
    return redirect(url_for('get_definitions'))

@app.route('/user_signup')
def user_signup():
        return render_template("user/signup.html")

@app.route('/user_login')
def user_login():
        return render_template("user/login.html")

@app.route('/user_edit')
def user_edit():
        return render_template("user/edit.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')), 
        debug=True)