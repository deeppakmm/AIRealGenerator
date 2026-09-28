from concurrent.futures import ThreadPoolExecutor
import json
from flask import Flask, jsonify, render_template, request, send_from_directory
import uuid
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import generate_process
from paths import REELS_FOLDER, UPLOAD_FOLDER

app = Flask(__name__)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
REELS_FOLDER.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
reel_executor = ThreadPoolExecutor(max_workers=1)


def write_job_status(upload_dir, status, message=None):
    status_data = {"status": status}
    if message:
        status_data["message"] = message

    temporary_path = upload_dir / "status.tmp"
    status_path = upload_dir / "status.json"
    temporary_path.write_text(json.dumps(status_data), encoding="utf-8")
    temporary_path.replace(status_path)


def process_reel(rec_id):
    upload_dir = UPLOAD_FOLDER / rec_id
    try:
        generate_process.start1(rec_id)
        write_job_status(upload_dir, "success")
    except Exception:
        app.logger.exception("Reel creation failed.")
        write_job_status(
            upload_dir,
            "error",
            "Reel creation failed. Check the server configuration and logs.",
        )


@app.errorhandler(RequestEntityTooLarge)
def handle_upload_too_large(error):
    return jsonify({"status": "error", "message": "The total upload is too large. Please use fewer or smaller photos."}), 413

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
                
        write_job_status(upload_dir, "processing")
        reel_executor.submit(process_reel, rec_id)

        return jsonify({"status": "processing", "job_id": rec_id}), 202

    # Show the page when the user opens it.
    return render_template("create.html")


@app.route("/create/status/<job_id>")
def create_status(job_id):
    try:
        rec_id = str(uuid.UUID(job_id))
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid reel job ID."}), 404

    status_path = UPLOAD_FOLDER / rec_id / "status.json"
    try:
        status_data = json.loads(status_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Reel job was not found."}), 404

    return jsonify(status_data)


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
