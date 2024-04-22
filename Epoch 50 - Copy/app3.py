from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    security = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(200), nullable=True)
    age = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(200), nullable=True)
    
db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def load_my_model():
    return load_model('dinesh.h5',compile=False)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        security = request.form['security']
        new_user = User(email=email,username=username, password=password,security=security)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard1', username=username))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('signin.html')

@app.route('/dashboard1/<username>', methods=['GET', 'POST'])
def dashboard1(username):
    user = User.query.filter_by(username=username).first()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        

        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if '.' not in file.filename:
            filename = secure_filename(file.filename) + '.jpg'
        else:
            filename = secure_filename(file.filename)
        if user is None:
            flash('User not found', 'danger')
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            my_model = load_my_model()

            img = image.load_img(filepath, target_size=(100, 100))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            feature_maps = my_model.predict(img_array)
            predictions = feature_maps[0]
            predicted_class_index = np.argmax(predictions)

            print(predicted_class_index)

            status=str(predicted_class_index)
            if status=="0":
                print("Cancer")
                ss="Cancer"
            elif status=="1":
                print("Dyed-lifted-polyps")
                ss="Dyed-lifted-polyps"
            elif status=="2":
                print("Dyed-resection-margin")
                ss="Dyed-resection-margin"
            elif status=="3":
                print("Esophagitis")
                ss="Esophagitis"
            elif status=="4":
                print("Normal-cecum")
                ss="Normal-cecum"
            elif status=="5":
                print("Normal-pylorus")
                ss="Normal-pylorus"
            elif status=="6":
                print("Normal-z-line")
                ss="Normal-z-line"
            elif status=="7":
                print("Polyps")
                ss="Polyps"
            else:
                print("Ulcerative-colitis")
                ss="Ulcerative-colitis"            
            user.name = name
            user.age = age
            user.gender = gender
            user.phone_number = phone_number
            user.status = ss
            db.session.commit()

            flash(f'Image uploaded and status predicted: {ss}', 'success')
            return redirect(url_for('output', username=username, name=name, age=age, gender=gender, 
                        phone_number=phone_number, filename=filename, status=ss))
            

    return render_template('dashboard1.html', user=user)
@app.route('/output/<username>/<name>/<age>/<gender>/<phone_number>/<filename>/<status>')
def output(username, name, age, gender, phone_number, filename, status):
    image_filename = filename if filename.endswith('.jpg') else filename + '.jpg'
    return render_template('output.html', username=username, name=name, age=age, gender=gender, phone_number=phone_number, status=status, image_filename=image_filename)

@app.route('/image_result')
def image_result():
    image_filename = filename if filename.endswith('.jpg') else filename + '.jpg'
    return send_file(image_filename, mimetype='image/jpg', as_attachment=False)
if __name__ == '__main__':
    app.run(debug=False)
