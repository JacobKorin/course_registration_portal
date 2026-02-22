from flask import Flask, request, jsonify
from pymongo import MongoClient
app = Flask(__name__)

uri="mongodb://localhost:27017/"
client = MongoClient(uri)

db = client.get_database("course_registration_portal")

@app.route("/courses", methods = ["GET"])
def list_courses():
    courses_collection = db.get_collection("courses")

    courses = list(courses_collection.find())

    return jsonify(courses),200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5100)
