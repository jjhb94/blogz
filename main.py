from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy # this is the ORM; sequel alchemy needs a connection string to do its job

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:!2B_brkn@localhost:8889/blogz' # this is the connection string 
app.config['SQLALCHEMY_ECHO'] = True # this will show the SQL queries; not necessary 
db = SQLAlchemy(app)  #making a new database object 

# here is where you will create a model
# the model creates a python object to create a blog class with properties (i.d., title, body)

class Blog(db.Model): # this creates a persistent class, or a class that can be stored in the data base 
    id = db.Column(db.Integer, primary_key=True)   # every class that is to be stored in a data base will have an id - a primary key
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body): # this is the constructor class and is necessary to initialize a class and its objects
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog {0}>'.format(self.title)

class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(25))
        password = db.Column(db.String(25))
        blogs = db.relationship('Blog', backref='owner') # this signifies the relationship between the blog table and this user, binding user to blog posts they write

        def __init__(self, username, password):
            self.username = username
            self.password = password 

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_name = request.form['blog']
        blog_body = request.form['body']
        
        new_blog = Blog(blog_name, blog_body)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?id={0}'.format(new_blog.id)) # this will return the new page after we hit submit

    blogs = Blog.query.all()
    return render_template('todos.html',title="Build a Blog", 
        blogs=blogs)

@app.route('/delete-blog-post', methods=['POST'])
def delete_posts():
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()
    return redirect('/')
@app.route('/blog', methods=['GET', 'POST'])
def home():
    id = request.args.get("id")
    '''now we make a conditional to return the blog post if the ID is in the URL, 
       or just the main page with the blog posts '''
    if id:  # if the ID is in the URL,
        blogs = Blog.query.filter_by(id=id).all() # grab all of the blog entries on the main page and return them
        return render_template('blog.html', title="Build a Blog", 
            blogs=blogs )
    else:

        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog",
            blogs=blogs)

@app.route('/')
def main_page():
    #if login is true:
    return redirect('/login')
    #else:
    # return redirect login.html 

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def verify_login():
    if request.method == 'POST':
        user = request.form['username']
        username_error = ''
        if user not in User.query.all():
            username_error = 'this username does not exist'
            return render_template('/login', valid_credentials=username_error)
        else:
            return render_template('base.html')



@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route("/signup", methods=['POST'])
def validate():

    user_name = request.form["User-name"] #this takes the number field and converts it into int
    username_error =''
    password_error =''

    user_password = request.form["Password"] # this takes what is is the text box and passes it to the the variable 
    confirm_password = request.form["Confirm-Password"]
    
    if (not user_name) or (' ' in user_name):
        username_error = 'That is not a valid username'
    if user_password != confirm_password:
        password_does_not_match = 'passwords do not match'
        password_error = 'that is not a valid password'
        return render_template('signup.html', valid_credentials=user_name, invalid_credentials=username_error, invalid_password=password_error, dont_match=password_does_not_match)
       
    else:
        new_user = User(user_name, user_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/newpost?id={0}'.format(new_user.id)) # this will return the new page after we hit submit



if __name__ == '__main__':   # this is a shield for the app.run() so that the code above is ONLY run when we run the main.py file directly
    app.run()               # it lets the program start if you want without running a full blown flask application. 