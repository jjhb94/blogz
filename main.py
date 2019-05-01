from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy # this is the ORM; sequel alchemy needs a connection string to do its job

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:!2B_brkn@localhost:8889/blogz' # this is the connection string 
app.config['SQLALCHEMY_ECHO'] = True # this will show the SQL queries; not necessary 
db = SQLAlchemy(app)  #making a new database object 
app.secret_key = '!@fj9d_jfN39s$'
# here is where you will create a model
# the model creates a python object to create a blog class with properties (i.d., title, body)

class Blog(db.Model): # this creates a persistent class, or a class that can be stored in the data base 
    id = db.Column(db.Integer, primary_key=True)   # every class that is to be stored in a data base will have an id - a primary key
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner): # this is the constructor class and is necessary to initialize a class and its objects
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog {0}>'.format(self.title)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True) # this limits the number of user names to be unique
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner') # this signifies the relationship between the blog table and this user, binding user to blog posts they write

    def __init__(self, username, password): # this is the constructor for the user class ( with necessary parameters)
        self.username = username 
        self.password = password 

@app.before_request
def require_login(): # this checks every request to make sure that the user HAS logged in
    allowed_routes = ['login', 'signup', 'home', 'main_page'    ] # this is essentially a white list for non-logged in users; else we get an endless 302 error loop 
    if request.endpoint not in allowed_routes and 'user' not in session: # if their is not a key called 'user' in the session dictionary; if the user is not logged in 
        return redirect('/login') # redirect to the login page

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['user']).first()

    if request.method == 'POST':
        blog_name = request.form['blog']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['user']).first()

        new_blog = Blog(blog_name, blog_body, owner)

        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?id={0}'.format(new_blog.id)) # this will return the new page after we hit submit

    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('todos.html',title="Blogz", 
        blogs=blogs, owner=owner)

@app.route('/blog', methods=['GET', 'POST'])
def home():
    blogs = Blog.query.all()
    # owner = User.query.filter_by(username=session['user']).first()
    id = request.args.get('id')
    user_id = request.args.get('user')

    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', blogs=blogs)

    
    '''now we make a conditional to return the blog post if the ID is in the URL, 
       or just the main page with the blog posts '''
    if id:  # if the ID is in the URL,
        blogs = Blog.query.filter_by(id=id).all() # grab all of the blog entries on the main page and return them
        return render_template('blog.html', title="Blogz", 
            blogs=blogs)
    else:
        return render_template('blog.html', title="Blogz",
            blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        passwd = request.form['password']
        account = User.query.filter_by(username=user).first() # this retrieves the first user with the username 
        if account and account.password == passwd: # this is convoluted, but detailed and it works for the signing in function
            session['user'] = user
            flash("Login successful")
            print(session)
            return redirect('/blog')
        elif account:
            password_error = 'Password is incorrect'
            return render_template('login.html', valid_credentials=user, invalid_password=password_error)
        else:
            # return why the login failed
            username_error = 'this user does not exist'
            return render_template('login.html', valid_credentials=user, invalid_credentials=username_error)
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user = request.form['User-name']
        passwd = request.form['Password']
        confirm_passwd = request.form['Confirm-Password']
        
        existing_account = User.query.filter_by(username=user).first()
        if not existing_account:
            if (not user) or (' ' in user):
                username_error= 'That is not a valid username'
            if passwd != confirm_passwd:
                password_does_not_match = 'passwords do not match'
                password_error = 'that is not a valid password'
                return render_template('signup.html', valid_credentials=user, invalid_credentials=username_error, invalid_password=password_error, dont_match=password_does_not_match)
            # add remember user has signed in
            new_account = User(user, passwd)
            db.session.add(new_account)
            db.session.commit()
            session['user'] = user
            return redirect('/newpost?id={0}'.format(new_account.id))
        else:
            username_error = 'This account already exists'
            return render_template('signup.html', valid_credentials=user, invalid_credentials=username_error)
        # need to validate user data 
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['user']
    flash("Successfully Logged Out")
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def main_page():
    if request.method== 'POST':
        blogs = Blog.query.filter_by(id=id)
        return render_template('singleUser.html', blog=blogs)
    users = User.query.all()
    blogs = Blog.query.filter_by(id=id)
    return render_template('index.html', users=users, blog=blogs)
    
    
    #else:
    # return redirect login.html 


if __name__ == '__main__':   # this is a shield for the app.run() so that the code above is ONLY run when we run the main.py file directly
    app.run()               # it lets the program start if you want without running a full blown flask application. 