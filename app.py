from flask import Flask, render_template, request, redirect, send_from_directory
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# صفحه اصلی
@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", files=files)


# آپلود امن‌تر
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]

        if file:
            # جلوگیری از اسم تکراری
            filename = str(uuid.uuid4()) + "_" + file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        return redirect("/")
    return render_template("upload.html")


# دانلود
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
