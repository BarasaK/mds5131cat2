from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

client = MongoClient("mongodb://localhost:27017/")
db = client["real_estate_db"]
properties = db["properties"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect('/listings')

@app.route('/add', methods=["GET", "POST"])
def add_property():
    if request.method == "POST":
        image_path = ""
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"uploads/{filename}"
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
        return redirect('/listings')
    return render_template("add_property.html")

@app.route('/listings')
def listings():
    all_properties = list(properties.find())
    return render_template("listings.html", listings=all_properties)

@app.route('/edit/<id>', methods=["GET", "POST"])
def edit_property(id):
    prop = properties.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        updated_data = {
            "name": request.form["name"],
            "location": request.form["location"],
            "price": float(request.form["price"]),
            "type": request.form["type"],
            "status": request.form["status"],
            "image": prop["image"]  # Keep existing image for now
        }
        properties.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        return redirect('/listings')
    return render_template("edit_property.html", prop=prop)

@app.route('/delete/<id>')
def delete_property(id):
    properties.delete_one({"_id": ObjectId(id)})
    return redirect('/listings')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(debug=True)
