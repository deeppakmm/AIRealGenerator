from flask import Flask, render_template, request, jsonify
import uuid
from werkzeug.utils import secure_filename
import os
import generate_process

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    # Handle data sent from the page with a POST request.
    if request.method == 'POST':
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        
        # Check that the description and files were sent.
        if not desc or desc.strip() == "" or not request.files:
            return jsonify({"status": "error", "message": "Missing description or files"}), 400
            
        input_files = []
        has_valid_file = False
        
        # Save each uploaded file.
        for key in request.files:
            file = request.files[key]
            
            if file and file.filename != '':
                has_valid_file = True
                filename1 = secure_filename(file.filename)
                filename1 = filename1.replace(" ", "_")
                
                # Create a folder for this upload and save the file.
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], rec_id), exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, filename1))
                input_files.append(filename1)
        
        # Return an error if no files were uploaded.
        if not has_valid_file:
            return jsonify({"status": "error", "message": "No valid files uploaded"}), 400
            
        # Save the description and file list.
        with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, 'desc.txt'), 'w') as f:
            f.write(desc)
            
        
        for fl in input_files:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, 'input.txt'), 'a') as f1:
                f1.write(f"file '{fl}'\nduration 1\n") 
                
    
        generate_process.start1()
        

        return jsonify({"status": "success", "message": "Your Reel is created!"})

    # Show the page when the user opens it.
    myId = uuid.uuid1()
    return render_template("create.html", myId=myId)

@app.route("/gallery")
def gallery():
    reels_directory = os.path.join(app.static_folder, "reels")
    reels = []

    if os.path.isdir(reels_directory):
        reels = sorted(
            (filename for filename in os.listdir(reels_directory) if filename.lower().endswith(".mp4")),
            key=lambda filename: os.path.getmtime(os.path.join(reels_directory, filename)),
            reverse=True,
        )

    return render_template("gallery.html", reels=reels)

if __name__ == "__main__":
    app.run(debug=True)
