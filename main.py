from flask import Flask, jsonify, render_template, request, send_from_directory
import uuid
import os
from werkzeug.utils import secure_filename
import generate_process
from paths import REELS_FOLDER, UPLOAD_FOLDER

app = Flask(__name__)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
REELS_FOLDER.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    # Handle data sent from the page with a POST request.
    if request.method == 'POST':
        desc = request.form.get("text")
        
        # Check that the description and files were sent.
        if not desc or desc.strip() == "" or not request.files:
            return jsonify({"status": "error", "message": "Missing description or files"}), 400
            
        rec_id = str(uuid.uuid4())
        upload_dir = UPLOAD_FOLDER / rec_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        input_files = []
        
        # Save each uploaded file.
        for key in request.files:
            file = request.files[key]
            
            if file and file.filename != '':
                filename1 = secure_filename(file.filename)
                if not filename1:
                    continue
                filename1 = filename1.replace(" ", "_")
                file.save(upload_dir / filename1)
                input_files.append(filename1)
        
        # Return an error if no files were uploaded.
        if not input_files:
            return jsonify({"status": "error", "message": "No valid files uploaded"}), 400
            
        # Save the description and file list.
        with open(upload_dir / "desc.txt", "w", encoding="utf-8") as f:
            f.write(desc)
            
        with open(upload_dir / "input.txt", "w", encoding="utf-8") as f1:
            for fl in input_files:
                f1.write(f"file '{fl}'\nduration 1\n") 
                
        try:
            generate_process.start1(rec_id)
        except Exception:
            app.logger.exception("Reel creation failed.")
            return jsonify({"status": "error", "message": "Reel creation failed. Check the server configuration and logs."}), 500

        return jsonify({"status": "success", "message": "Your Reel is created!"})

    # Show the page when the user opens it.
    return render_template("create.html")

@app.route("/gallery")
def gallery():
    reels = []

    if REELS_FOLDER.is_dir():
        reels = sorted(
            (filename for filename in REELS_FOLDER.iterdir() if filename.suffix.lower() == ".mp4"),
            key=lambda filename: filename.stat().st_mtime,
            reverse=True,
        )
        reels = [filename.name for filename in reels]

    return render_template("gallery.html", reels=reels)


@app.route("/reels/<path:filename>")
def reel_file(filename):
    return send_from_directory(REELS_FOLDER, filename, mimetype="video/mp4", conditional=True)


@app.route("/reels/<filename>/download")
def download_reel(filename):
    return send_from_directory(
        REELS_FOLDER,
        filename,
        mimetype="video/mp4",
        as_attachment=True,
        download_name=filename,
        conditional=True,
    )


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
