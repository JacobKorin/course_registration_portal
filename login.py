from flask import Flask, request, jsonify
from pymongo import MongoClient
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import os
from dotenv import load_dotenv
from bson import ObjectId
from flask_cors import CORS
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)

ph = PasswordHasher()


uri="mongodb://localhost:27017/"
client = MongoClient(uri)

db = client.get_database("course_registration_portal")
users = db.get_collection("users")


@app.route("/auth/register", methods = ["POST"])
def register():
    username = request.form["username"]
    password = ph.hash(request.form["password"])

    role = request.form["role"]

    user = {"username": username, "hash_password":password, "role":role}

    users.insert_one(user)

    return jsonify({"status": "success"}),201

@app.route("/auth/login", methods = ["POST"])
def login():
    try:
        user = users.find_one({"username":request.form["username"]})
        user["_id"] = str(user["_id"])
        ph.verify(user["hash_password"], request.form["password"])

        access_token = create_access_token(identity=user["_id"], additional_claims={"role": user["role"]})
        return jsonify(access_token=access_token), 200
    except:
        return jsonify({"error":"invalid password"}),400
 
@app.route("/auth/me", methods = ["GET"])
@jwt_required()
def current_user():

    user = ObjectId(get_jwt_identity())
    document = users.find_one({"_id":user},{"hash_password":0})
    document["_id"] = str(document["_id"])
    
    return jsonify(document),200

if __name__ =='__main__':
    app.run(host='0.0.0.0',port=5000)