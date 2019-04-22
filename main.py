from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy # this is the ORM; sequel alchemy needs a connection string to do its job

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:!2b_brkn@localhost:8889/build-a-blog' # this is the connection string 
app.config['SQLALCHEMY_ECHO'] = True # this will show the SQL queries; not necessary 
db = SQLAlchemy(app)  #making a new database object 

# here is where you will create a model
# the model creates a python object to create a blog class with properties (i.d., title, body)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body): # this is the constructor class and is necessary to initialize a class and its objects
        self.title = title
        self.body = body
    def __repr__(self):
        return '<Blog {0}>'.format(self.title)

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_name = request.form['blog']
        blog_body = request.form['body']
        
        new_blog = Blog(blog_name, blog_body)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('todos.html',title="Build a Blog", 
        blogs=blogs)

@app.route('/blog')
def home():
    blogs = Blog.query.all()
    return render_template('base.html', title="Build a Blog", completed_blogs=blogs, blogs=blogs)

if __name__ == '__main__':
    app.run()