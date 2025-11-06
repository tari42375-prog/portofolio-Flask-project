# import flask
from flask import Flask, render_template, session, request, redirect, url_for
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
import MySQLdb.cursors

# main app
app = Flask(__name__)
app.secret_key = '@#$%'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] = 'portofolio'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# set route untuk /
@app.route('/')
def public():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users LIMIT 1")
    profil = cur.fetchone()

    cur.execute("SELECT * FROM skills")
    skills = cur.fetchall()

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    cur.close()
    return render_template('public.html', profil=profil, skills=skills, projects=projects)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['inpUsername']
        password = request.form['inpPassword']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username =%s AND password =%s", (username,password))
        result = cur.fetchone()
        cur.close()
        if result:
            session['is_logged_in'] = True
            session['username'] = result[1]
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
        session.pop('is_logged_in', None)
        session.pop('username', None)
    
        return redirect(url_for('public'))

@app.route("/home")

def home():
    if 'is_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (session['username'],))
        profil = cur.fetchone()

        cur.execute("SELECT * FROM skills")
        skills = cur.fetchall()

        cur.execute("SELECT * FROM projects")
        projects = cur.fetchall()

        cur.close()
        return render_template('home.html', profil=profil, skills=skills, projects=projects)
    else:
        return redirect(url_for('login'))


@app.route("/edit_profile", methods=['POST', 'GET'])
def edit_profile():
    if 'is_logged_in' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        bio = request.form['bio']
        file = request.files['photo']

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            photo_path = f'uploads/{filename}'
        else:
            cur.execute("SELECT photo FROM users WHERE username=%s", (username,))
            photo_path = cur.fetchone()[0]

        cur.execute("UPDATE users SET name=%s, bio=%s, photo=%s WHERE username=%s", (name, bio, photo_path, username))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))
    
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    profil = cur.fetchone()
    cur.close()
    return render_template('edit_profile.html', profil=profil)



@app.route("/add_skills", methods=['POST'])
def add_skills():
    if 'is_logged_in' in session and request.method == 'POST':
        name = request.form['name']
        level = request.form['level']

        icon_file = request.files.get('icon')
        icon_filename = None

        if icon_file and icon_file.filename != '':
            filename = secure_filename(icon_file.filename)
            icon_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            icon_file.save(icon_path)
            icon_filename = f'uploads/{filename}'

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO skills (name, level, icon) VALUES (%s, %s, %s)", (name, level, icon_filename))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))

@app.route("/delete_skills/<int:id>")
def delete_skills(id):
    if 'is_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM skills WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))

@app.route("/update_skills/<int:id>", methods=['POST'])
def update_skills(id):
    if 'is_logged_in' in session and request.method == 'POST':
        name = request.form['new_name']
        level = request.form['new_level']

        icon_file = request.files['icon']
        icon_filename = None

        if icon_file and icon_file.filename != '':  
            filename = secure_filename(icon_file.filename)
            icon_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            icon_file.save(icon_path)
            icon_filename = f'uploads/{filename}'

            cur = mysql.connection.cursor()
            cur.execute("UPDATE skills SET name=%s, level=%s, icon=%s WHERE id=%s", (name, level, icon_filename, id))
            mysql.connection.commit()
            cur.close()

        cur = mysql.connection.cursor()
        cur.execute("UPDATE skills SET name=%s, level=%s WHERE id=%s", (name, level, id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))

@app.route("/add_projects", methods=['POST'])
def add_projects():
    if 'is_logged_in' in session and request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        link = request.form['link']
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = f'uploads/{filename}'

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO projects (title, description, link, image) VALUES (%s, %s, %s, %s)", (title, description, link, image_filename))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))

@app.route("/delete_projects/<int:id>")
def delete_projects(id):
    if 'is_logged_in' in session:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM projects WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))

@app.route("/update_projects/<int:id>", methods=['POST'])
def update_projects(id):
    if 'is_logged_in' in session and request.method == 'POST':
        title = request.form['new_title']
        description = request.form['new_description']
        link = request.form['new_link']
        image_file = request.files['image']
        image_filename = None
        if image_file and image_file.filename != '':  
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = f'uploads/{filename}'

            cur = mysql.connection.cursor()
            cur.execute("UPDATE projects SET title=%s, description=%s, link=%s, image=%s WHERE id=%s", (title, description, link, image_filename, id))
            mysql.connection.commit()
            cur.close()

        cur = mysql.connection.cursor()
        cur.execute("UPDATE projects SET title=%s, description=%s WHERE id=%s", (title, description, id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))

if __name__ =="__main__":
    app.run(debug=True)