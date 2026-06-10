from flask import Flask, render_template, request, redirect, send_from_directory
import os

app = Flask(__name__)

# پوشه ذخیره فایل‌ها
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# صفحه اصلی (نمایش فایل‌ها)
@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", files=files)


# آپلود فایل
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return redirect("/")
    return render_template("upload.html")


# دانلود فایل
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
