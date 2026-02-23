from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import timedelta, datetime,timezone
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, jwt_required, get_jwt_identity
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

uri="mongodb://localhost:27017/"
client = MongoClient(uri)

db = client.get_database("course_registration_portal")
courses_collection = db.get_collection("courses")
registration_collection = db.get_collection("registrations")

@app.route("/courses", methods = ["GET"])
def list_courses():
    courses = list(courses_collection.find())

    for course in courses:
        course["_id"] = str(course["_id"])
        course["professor_id"] = str(course["professor_id"])

    return jsonify(courses),200

@app.route("/courses", methods = ["POST"])
@jwt_required()
def create_course():
    role = get_jwt()["role"]

    if role == "professor":
        caller = ObjectId(get_jwt_identity())
        course_code = request.form["course_code"]

        course = {"professor_id":caller,"course_code":course_code}
        courses_collection.insert_one(course)

        return jsonify({"status":"success"}),201
    else:
        return jsonify({"error":"insufficient permissions"}),403
    
@app.route("/courses/<course_id>/register", methods = ["POST"])
@jwt_required()
def course_register(course_id):
    course_id = ObjectId(course_id)

    if courses_collection.find_one({"_id":course_id}):
        caller = ObjectId(get_jwt_identity())
        timestamp = datetime.now(timezone.utc)
        
        registration = {"course_id":course_id,"student_id":caller,"registration_date":timestamp}
        registration_collection.insert_one(registration)
        
        return jsonify({"status":"success"}),201
    else:
        return jsonify({"error":"course ID not found"}),404
    
@app.route("/courses/<course_id>/register", methods = ["DELETE"])
@jwt_required()
def course_deregister(course_id):
    course_id = ObjectId(course_id)

    if courses_collection.find_one({"_id":course_id}):
        caller = ObjectId(get_jwt_identity())
        registration_collection.delete_one({"course_id":course_id, "student_id":caller})

        return jsonify({"status":"delete successful"}),200
    else:
        return jsonify({"error":"course ID not found"}),404
    
@app.route("/courses/<course_id>/registrants", methods = ["GET"])
@jwt_required()
def all_registrants(course_id):
    role = get_jwt()["role"]

    if role == "professor":
        course_id = ObjectId(course_id)
        caller = ObjectId(get_jwt_identity())

        course = courses_collection.find_one({"_id":course_id})
        
        if course:
            if course["professor_id"] == caller:
                registrants = list(registration_collection.find({"course_id":course_id},{"_id":0}))

                for registrant in registrants:
                    registrant["course_id"] = str(registrant["course_id"])
                    registrant["registration_date"] = str(registrant["registration_date"])
                    registrant["student_id"] = str(registrant["student_id"])

                return jsonify(registrants), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5100)
