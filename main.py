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

    def __init__(self, title, body, owner): # this is the constructor class and is necessary to initialize a class and its objects
        self.title = title
        self.body = body
        self.owner = owner
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


if __name__ == '__main__':   # this is a shield for the app.run() so that the code above is ONLY run when we run the main.py file directly
    app.run()               # it lets the program start if you want without running a full blown flask application. 