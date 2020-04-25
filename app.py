import os
from flask import Flask, render_template, redirect, request, url_for 
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_DBNAME"]= 'BIMDefinitions'
app.config["MONGO_URI"] = os.environ.get('MONGODB_TERMS')
#app.config["MONGO_URI"] = 'mongodb+srv://AllardDB:RxBuROru0OyhHyMC@gcpbelgium-fdk0n.gcp.mongodb.net/BIMDefinitions?retryWrites=true&w=majority'

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
    definitions.insert_one(request.form.to_dict())
    return redirect(url_for('get_definitions'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)