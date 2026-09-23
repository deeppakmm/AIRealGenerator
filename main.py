from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os



UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myId = uuid.uuid1()
    if(request.method=='POST'):
        print(request.files)
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        input_files = []
        for key, values in request.files.items():
            print(key, " : ", values)
            file = request.files[key]
            
            print(file)
            if file:
                filename1 = secure_filename(file.filename)
                filename1 = filename1.replace(" ", "_")
                # if(not(os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], rec_id)))):
                #     os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], rec_id))
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], rec_id), exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, filename1))
                input_files.append(filename1)
            
        with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, 'desc.txt'), 'w') as f:
            f.write(desc)
        for fl in input_files:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, 'input.txt'), 'a') as f1:
                f1.write(f"file '{fl}'\nduration 1\n") 


    return render_template("create.html", myId=myId)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

app.run(debug=True)