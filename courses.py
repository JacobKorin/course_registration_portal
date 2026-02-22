from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity
import os
from dotenv import load_dotenv
from bson import ObjectId
load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

jwt = JWTManager(app)

uri="mongodb://localhost:27017/"
client = MongoClient(uri)

db = client.get_database("course_registration_portal")

@app.route("/courses", methods = ["GET"])
def list_courses():
    courses_collection = db.get_collection("courses")

    courses = list(courses_collection.find())

    for course in courses:
        course["_id"] = str(course["_id"])
        course["professor_id"] = str(course["professor_id"])
        
    return jsonify(courses),200

@app.route("/courses", methods = ["POST"])
@jwt_required()
def create_course():
    courses_collection = db.get_collection("courses")
    role = get_jwt()["role"]

    if role == "professor":
        caller = ObjectId(get_jwt_identity())
        course_code = request.form["course_code"]

        course = {"professor_id":caller,"course_code":course_code}
        courses_collection.insert_one(course)

        return jsonify({"status":"success"}),201
    else:
        return jsonify({"error":"insufficient permissions"}),403
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5100)
