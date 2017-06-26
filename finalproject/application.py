import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory, send_file, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime
from werkzeug.utils import secure_filename
from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


UPLOAD_FOLDER = 'users/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

photo_path = []
@app.route("/search", methods=["POST", "GET"])
@login_required
def search():
    if request.method == "POST":
        searched =  '%' + request.form.get("sear") + '%'
        
        if not searched:
            return ('not a valid search', 404)
        tag = db.execute("SELECT projname FROM tag WHERE projname LIKE :searching_for OR user LIKE :searching_for OR tags LIKE :searching_for", searching_for = searched)
        name = db.execute("SELECT user FROM tag WHERE projname LIKE :searching_for OR user LIKE :searching_for OR tags LIKE :searching_for", searching_for = searched)
        
        project = []
        i = 0
        while True:
            try:
                project.append(tag[i]["projname"] + ".jpg")
                photo_path.append('users/' + name[i]["user"] + '/' + tag[i]["projname"] + '/' + tag[i]["projname"] + ".jpg")
                project.append(tag[i]["projname"].upper())
                y = open('users/' + name[i]["user"] + '/' + tag[i]["projname"] + '/' + 'aainstructions.txt').read()
                project.append(y)
                i += 1
            except IndexError:
                break
        return render_template("result.html", result_projects = project)
    else:
        return ('not requested', 204)
        
@app.route('/result/<filename>')
def send_photo(filename):
    for i in range(0, len(photo_path)):
            if filename in photo_path[i]:
                x = photo_path[i].replace(filename, '')
                path = x 
    
    return send_from_directory(path, filename)
    
@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        name = db.execute("SELECT name FROM users WHERE id = :id", id = session["user_id"])
        namn = name[0]["name"]
        
        projectname = request.form.get("pname")
        projecttag = request.form.get("tag")
        if not projectname and not projecttag:
            return ('', 204)
        path = 'users/' + namn + '/'
        if not os.path.exists(path + projectname):
            os.makedirs(path + projectname)
        path += projectname + '/'
        
        tags = db.execute("SELECT user FROM tag WHERE projname = :projname", projname = projectname)
        if not tags:
            db.execute("INSERT INTO tag (user, tags, projname) VALUES (:user, :tag, :projname)", user = name[0]["name"], 
                tag = projecttag, projname = projectname)
        
        if 'file' not in request.files:
            flash('No file part')
            return ('', 204)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return  
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(path, projectname + ".jpg" ))
        instructions = request.form.get("instructions")
        if not instructions:
            return ('', 204)
        if not os.path.exists(path + "aainstructions.txt"):
            os.mknod(path + "aainstructions.txt")
        else:
            os.remove(path + "aainstructions.txt")
            os.mknod(path + "aainstructions.txt")
        path = path + "aainstructions.txt"
        with open(path, 'a') as out:
            out.write(instructions + '\n')
        return ('', 204)
           
    else:     
        return render_template("upload.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



image_path = []
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    name = db.execute("SELECT name FROM users WHERE id = :id", id = session["user_id"])
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for("upload"))
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + name[0]["name"], str(session["user_id"]) + ".jpg" ))
    
    
    path = 'users/' + name[0]["name"] + '/' 
    image = str(session["user_id"]) + ".jpg"
    instruct = []
    
    for path, subdirs, files in os.walk(path):
        for x in files:
            if x.endswith(".txt") == True:
                new_path = os.path.join(path, x)
                y = open(new_path).read()
                instruct.append(y)
            elif x.endswith(".jpg") == True:
                if x != image:
                    instruct.append(x)
                    image_path.append(os.path.join(path, x))
    return render_template("profile.html", username = name[0]["name"], image_name = image, feeds = instruct)

@app.route('/profile/<filename>')
def send_image(filename):
    name = db.execute("SELECT name FROM users WHERE id = :id", id = session["user_id"])
    path = 'users/' + name[0]["name"] + '/'
    if filename == str(session["user_id"]) + ".jpg":
        return send_from_directory(path, filename)
    else: 
        for i in range(0, len(image_path)):
            if filename in image_path[i]:
                x = image_path[i].replace(filename, '')
                path = x 
        return send_from_directory(path, filename)
    
    

@app.route('/login', methods=['GET', 'POST'])
def login():
   # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # ensure username was submitted
        if not username:
            return render_template("login.html", username="Not a valid username")

        # ensure password was submitted
        elif not password:
            return render_template("login.html", username="Not a valid password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE name = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("login.html", username="No such user!")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
 
@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        users = db.execute("SELECT name FROM users")
        
        if not username or not username.isalpha():
            return render_template("register.html", username="Username not valid")
                
        # ensure password was submitted
        elif not request.form.get("password") or len(password) < 6:
            return render_template("register.html", password="Password not valid")
            
        elif not request.form.get("password") == request.form.get("password1"):
            return render_template("register.html", username="Passwords dosen't match")
        
        valid = db.execute("SELECT id FROM users WHERE name = :name", name = username)
        if valid: 
            return render_template("register.html", username="Username exicts")
        
        result = db.execute("INSERT INTO users (name, hash) VALUES(:user, :hash)", 
            user=request.form.get("username"), 
            hash=pwd_context.encrypt(request.form.get("password")))
            
        if not result:
            return render_template("register.html", username="Try again!")
        
        session["user_id"] = request.form.get("username")
        os.makedirs("users/" + session["user_id"])
        return redirect(url_for("index"))
    else:
        return render_template("register.html")
 
