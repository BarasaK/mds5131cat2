import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["real_estate_db"]
properties = db["properties"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect('/add')

@app.route('/add', methods=["GET", "POST"])
def add_property():
    if request.method == "POST":
        file = request.files["image"]
        image_path = ""

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)

        new_property = {
            "name": request.form["name"],
            "location": request.form["location"],
            "price": float(request.form["price"]),
            "type": request.form["type"],
            "status": request.form["status"],
            "image": image_path
        }
        properties.insert_one(new_property)
        return "✅ Property added successfully!"
    return render_template("add_property.html")
