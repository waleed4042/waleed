# to use flask ,render html templates, and also using request module like post and get 
from flask import Flask, render_template, request,session,redirect
# to connect flask app  with database 
from flask_sqlalchemy import SQLAlchemy
import math
import os
from werkzeug.utils import secure_filename
# to use time methods 
from datetime import datetime
# to use json files and parsing the json file to string and viceversa 
import json
# use file i/o to read json file and access the json object 
with open('templates/config.json','r') as c:
# first make a variable& parse json file like c and then access their object like params 
    parameters=json.load(c)["params"]
# make variable and make a condition with variable means if yes but in real app 
# we will provide proper address  
local_server=True
# make a flask app and pass argument __name__ 
app = Flask(__name__)
# secret key is used to secure the session data
app.secret_key='super-secret-key'
# applying codition if it runs from local_server then local uri of json 
app.config['UPLOAD_FOLDER']=parameters['upload_location']
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = parameters['local_uri'] 
# applying codition if it runs from other_server then server uri of json 
else:
        app.config['SQLALCHEMY_DATABASE_URI'] = parameters['server_uri']
# create an instance of class (SQLAlchemy with arg app) to use the properties of 
# SQLAlchemy and is uses to connect with databases
db = SQLAlchemy(app)

# this class actually bring database columns to here and we can use with html
# contacts class inherit from db.model 
# When you define this class in your Flask app, SQLAlchemy translates it
#  into a corresponding table in the database.
#  The class attributes (sno, name, phone_num, etc.) become the columns of the table
class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
# In this section, you're defining the columns of the table. Each db.Column represents a
#     column in the database
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    mess = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
class Posts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug= db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_update = db.Column(db.String(12), nullable=True)

@app.route("/")
def home():
#  used to fetch the data/post from the database and show it on the home page
    posts=Posts.query.filter_by().all()
    # here we calculate the number of pages like last page number
    last=math.ceil(len(posts)/int(parameters['no_of_post']))
    # [0:parameters['no_of_post']]
    # Pagination logic If the URL does not include a page parameter (e.g., http://example.com/), page will be None.
# str(page) will then be 'None', which is not numeric.
# So, not str(page).isnumeric() will be True, and the code page = 1 will run, setting page to 1.
# this is used to get the args from the url and if the page is not numeric then it will set the page to 1
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    # this will convert the page to integer
    page=int(page)
    # this helps us to fetch the index of the post from the database the post which need to be shown on the page if the page is 1 then it will show the first 5 post and if the page is 2 then it will show the next 5 post and so on
    posts=posts[(page-1)*int(parameters['no_of_post']):(page-1)*int(parameters['no_of_post'])+int(parameters['no_of_post'])]
    # first page
    if(page==1):
        prev='#'
        next='/?page='+str(page+1)
    elif(page==last):
        prev='/?page='+str(page-1)
        next='#'
    else:
        prev='/?page='+str(page-1)
        next='/?page='+str(page+1)    
    
    return render_template('index.html',param=parameters ,posts=posts,prev=prev,next=next)


@app.route("/about")
def about():
    return render_template('about.html',param=parameters)

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_first(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',param=parameters,post=post)
# GET is used to request data from the server.eg when you first load the contact form
# POST is used to send data to the server. When you submit the form, 
# it uses POST to send the data entered by the user to the server.
@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']==parameters['Admin_name']):
        if request.method=='POST':
            box_title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            if sno=='0':
                post=Posts(title=box_title,slug=slug,content=content,tagline=tline,img_update=img_file,date=datetime.now())
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.tagline=tline
                post.img_update=img_file
                post.date=datetime.now()
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',param=parameters ,sno=sno ,post=post)
@app.route('/Logout')
def logout():
    session.pop('user')
    return redirect('/login')
@app.route('/Delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']==parameters['Admin_name']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/login')
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database from html template'''
# request.form.get('name'): This retrieves the value of the form field with the 
# name attribute 'name' and variable like name,email holds the value come
# from the html form 
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
# This line creates a new instance of the Contacts class with the retrieved form data. 
        # It assigns values to the columns defined in your Contacts class.
        entry = Contacts(name=name, phone_num = phone, mess = message, date= datetime.now(),email = email )
    #    db.session.add(entry): This adds the new entry to the database session.
        db.session.add(entry)
        # db.session.commit(): This commits the transaction, saving the
        #  new entry to the database
        db.session.commit()
    return render_template('contact.html' ,param=parameters)
@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if ('user' in session and session['user']==parameters['Admin_name']):
        if request.method=='POST':
          f=request.files['file1']
          f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
          return "Uploaded Successfully"
@app.route("/login",methods=['GET','POST'])
def Login():
    
    if ('user' in session and session['user']==parameters['Admin_name']):
        posts=Posts.query.all()
        return render_template('dashboard.html',param=parameters,posts=posts)
    if(request.method=='POST'):
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if(username==parameters['Admin_name'] and userpass==parameters['Admin_password'] ):
            posts=Posts.query.all()
            session['user']=username
            return render_template('dashboard.html',param=parameters ,posts=posts)  
    else:
      return render_template('login.html',param=parameters)
# print(dir(SQLAlchemy))
app.run(debug=True) 



