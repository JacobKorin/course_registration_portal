from flask import Flask, request, jsonify
from pymongo import MongoClient
from argon2 import PasswordHasher


app = Flask(__name__)
ph = PasswordHasher()


uri="mongodb://localhost:27017/"
client = MongoClient(uri)

db = client.get_database("course_registration_portal")
users = db.get_collection("users")


@app.route("/auth/register", methods = ["POST"])
def register():
    id = len(list(users.find()))+1
    username = request.form["username"]
    password = ph.hash(request.form["password"])

    role = request.form["role"]

    user = {"_id":id,"username": username, "hash_password":password, "role":role}

    users.insert_one(user)

    return jsonify({"status": "success"}),201
if __name__ =='__main__':
    app.run(host='0.0.0.0',port=5000)