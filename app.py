from flask import Flask, render_template, request, redirect, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Song, Like, Comment
import os, uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ---------------- HOME ----------------
@app.route("/")
def index():
    songs = Song.query.all()
    return render_template("index.html", songs=songs)


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


# ---------------- UPLOAD (ADMIN ONLY) ----------------
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if not current_user.is_admin:
        return "Access denied"

    if request.method == "POST":
        file = request.files["file"]

        if file:
            filename = str(uuid.uuid4()) + "_" + file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            song = Song(filename=filename, title=file.filename)
            db.session.add(song)
            db.session.commit()

        return redirect("/")

    return render_template("upload.html")


# ---------------- SONG PAGE ----------------
@app.route("/song/<int:song_id>")
def song(song_id):
    song = Song.query.get_or_404(song_id)
    song.views += 1
    db.session.commit()

    comments = Comment.query.filter_by(song_id=song_id).all()
    return render_template("song.html", song=song, comments=comments)


# ---------------- LIKE ----------------
@app.route("/like/<int:song_id>")
@login_required
def like(song_id):
    exist = Like.query.filter_by(user_id=current_user.id, song_id=song_id).first()

    if not exist:
        db.session.add(Like(user_id=current_user.id, song_id=song_id))
        db.session.commit()

    return redirect(f"/song/{song_id}")


# ---------------- COMMENT ----------------
@app.route("/comment/<int:song_id>", methods=["POST"])
@login_required
def comment(song_id):
    c = Comment(
        user_id=current_user.id,
        song_id=song_id,
        text=request.form["text"]
    )
    db.session.add(c)
    db.session.commit()
    return redirect(f"/song/{song_id}")


# ---------------- DOWNLOAD ----------------
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
