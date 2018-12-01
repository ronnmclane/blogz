from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
#note for future: in actual web applications, secret keys should be kept secret, not included in github
#app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    deleted = db.Column(db.Boolean)
    owner_id = db. Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.deleted = False
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    #hashing/salting to be added in future version
    password = db.Column(db.String(36))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blogreader', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET'])
def index():
    userlist = User.query.all()
    return render_template('index.html', title="User List", userlist = userlist)


@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("No such username")
            return redirect("/login")
        elif user.password != password:
            flash("Incorrect password")
            return redirect("/login")
        else:
            session['username'] = username
            flash("Logged in")
            return redirect("/newpost")
    return render_template("login.html", title="Log In")


@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already in use", "error")
            return redirect("/signup")
        elif not (username and password and verify):
            flash("You must fill out all fields", "error")
            return redirect("/signup")
        elif len(username) < 3:
            flash("Username is too short", "error")
            return redirect("/signup")
        elif password != verify:
            flash("Password entries must match", "error")
            return redirect("/signup")
        elif len(password) < 3:
            flash("Password is too short", "error")
            return redirect("/signup")
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("You've been registered", "success")
            return redirect("/newpost")
    return render_template("signup.html", title="Register", username="")


@app.route('/blog', methods=['GET'])
def blogreader():
    #if blog was passed a blog id that exists, it will go to that individual blog post, otherwise, it will check for user id and if there is none, it goes to the main blog page that lists all.
    blogid = request.args.get("id")
    blog = Blog.query.filter_by(id = blogid).first()
    if blog:
        return render_template('individualpost.html', title=blog.title, blog=blog)
    else:
        #if blog was passed a userid that exists, it will go to that user's blog list. blogid takes priority.
        userid = request.args.get("user")
        user = User.query.filter_by(id = userid).first()
        if user:
            blogs = Blog.query.filter_by(owner_id = user.id).all()
            return render_template('individualuser.html', title=user.username, user=user, blogs=blogs)
        else:
            blogs = Blog.query.filter_by(deleted=False).all()
            return render_template('blogreader.html', title="All Blog Posts", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def blogwriter():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if blog_title == '':
            title_error = 'You must enter a title for your blog post.'
        else:
            title_error = ''
        if blog_body == '':
            body_error = 'You must enter content for your blog post.'
        else:
            body_error = ''
        if title_error == '' and body_error == '':
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id="+str(new_blog.id))
        else:
            return render_template('blogwriter.html', title="Create New Blog Post", blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)
    blogs = Blog.query.filter_by(deleted=False).all()
    return render_template('blogwriter.html', title="Create New Blog Post", blogs=blogs)


if __name__ == '__main__':
    app.run()