from flask import Flask, request, redirect, render_template, session, flash

from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'

app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'l3k8uuIoC9K4hj&jk'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120))

    body = db.Column(db.String(2000))

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))



    def __init__(self, title, body, owner):

        self.title = title

        self.body = body

        self.owner = owner





class User(db.Model):



    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(120))

    blogs = db.relationship('Blog', backref='owner')



    def __init__(self, username, password):

        self.username = username

        self.password = password





@app.before_request

def require_login():

    allowed_routes = ['login', 'signup', 'list_blogs', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:

        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:

            session['username'] = username

            flash("Logged in")

            return redirect('/newpost')

        else:

            error='User password incorrect, or user does not exist'

            go_back='"/login"'

            return render_template('error.html', error=error, go_back=go_back)



    return render_template('login.html')



@app.route('/logout')

def logout():

    del session['username']

    return redirect('/blog')



def valid_password(password):

    space = password.count(' ')

    count = len(password)

    if space == 0:

        if 3<=count and count<=120:

            return True

    else:

        return False



def valid_verify(password, verify):

    if password==verify:

        return True

    else:

        return False



def valid_username(username):

    space = username.count(' ')

    if space == 0:

        if len(username) >=3 and len(username) <= 20:

            return True

    else:

        return False



@app.route('/signup', methods=['POST', 'GET'])

def signup():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        verify = request.form['verify']



        username_error = ''

        password_error = ''

        verify_error = ''



        if not valid_username(username):

            username_error = "Please enter a username between 3 and 120 charachters with no spaces."

        if not valid_password(password):

            password_error = "Password must be between 3 and 120 characters and contain no spaces."

        if not valid_verify(password, verify):

            verify_error = "Passwords must match."



        if len(username_error)+len(password_error)+len(verify_error)!=0:

            return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error)



        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:

            new_user = User(username, password)

            db.session.add(new_user)

            db.session.commit()

            session['username'] = username

            return redirect('/newpost')

        else:

            error='This username is already taken.'

            go_back='"/signup"'

            return render_template('error.html', error=error, go_back=go_back)

            



    return render_template('signup.html')



@app.route("/newpost")

def newpost():

    

    return render_template('new-post.html')



@app.route("/newpost", methods=['POST'])

def validate_input():

    title = request.form.get('title')

    body = request.form.get('body')

    username = session['username']

    owner = User.query.filter_by(username=username).first()

    title_error = ''

    body_error = ''

    

    if title.isspace():

        title_error = "Title cannot be blank."

    

    if body.isspace():

        body_error = "Body cannot be blank."



    if not title_error and not body_error:

        print("starting new blog with {0}, {1}".format(title, body))

        new_blog = Blog(title, body, owner)

        db.session.add(new_blog)

        db.session.commit()

        return render_template('post.html', title=title, body=body, id=owner.id, username=username)

    else: 

        return render_template('new-post.html', title=title, body=body, title_error=title_error, body_error=body_error)


@app.route("/post", methods=['POST']) 

def post():

    username = session['username']

    print("USERNAME -----: " + username)

    owner = User.query.filter_by(username=username).first()

    title = request.form.get('title')

    body = request.form.get('body')

    return render_template('post.html', title = title, body=body, username=username, id=owner.id)



@app.route('/post', methods=['GET'])

def view_post():  

    id_number = request.args.get('id') 

    veiw_blog = Blog.query.get(id_number)

    title = veiw_blog.title

    body = veiw_blog.body   

    username= veiw_blog.owner.username

    id = veiw_blog.owner.id

    #return render_template('test.html', x=username)

    return render_template('post.html', title = title, body=body, username=username, id=id)



@app.route("/")  #Index of All Users

def index():

    users= User.query.all()

    return render_template('index.html', users=users)


@app.route("/blog") #All-Blog

def list_blogs():

    blog = Blog.query.order_by(Blog.id.desc()).all()

    username = 'All'

    return render_template('blog.html', username=username, blog=blog)





@app.route("/my_blog")

def blog():

    owner = User.query.filter_by(username=session['username']).first()

    blog = Blog.query.filter_by(owner=owner).order_by(Blog.id.desc()).all()

    username = owner.username

    return render_template('blog.html', blog=blog, username=username)







@app.route('/userblog', methods=['POST', 'GET'])

def user_blog(): 

    id = request.args['id']

    owner = User.query.filter_by(id=id).first()

    blog = Blog.query.filter_by(owner_id=owner.id).order_by(Blog.id.desc()).all()

    print(id)

    #return render_template('test.html', x=username)

    return render_template('blog.html', blog=blog, username= owner.username)

   

    







if __name__=='__main__':

    app.run()