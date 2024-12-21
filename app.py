from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import secrets
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)


app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'


client = MongoClient('mongodb://localhost:27017/')
db = client['Blogs']
blogs_collection = db['posts']
users_collection = db['users']


# @app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    
    posts = blogs_collection.find({})
    posts = [
        {
            "_id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "image": post.get("image", ""),
            "date": post["date"].strftime("%Y-%m-%d %H:%M:%S"),
            "comments": [
                {
                    "comment" : comment["comment"],
                    "author" : comment["author"],
                    "date" : comment["date"].strftime("%Y-%m-%d %H:%M:%S")
                }
                
                for comment in post.get("comments", [])
            ]
        }
        for post in posts
    ]
    
    if request.method == "POST":
        comment = request.form.get('content')
        post_id = request.form.get('post_id')
        author = request.form.get('author_name')
        
        comment_details = {
            "comment": comment,
            "author": author,
            "date": datetime.now()
            
        }
        
        # blog_post = blogs_collection.find_one({"_id":ObjectId(post_id)})
        
        blogs_collection.update_one(
            {"_id":ObjectId(post_id)},
            {"$push": {"comments": comment_details}}
        )
        
        return redirect (url_for('home'))
        
    
    return render_template('index.html', posts=posts)

@app.route('/create_post', methods = ['GET', 'POST'])
def create_post():
    if request.method == 'GET':
        return render_template('create_post.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.files.get('image')
        
        
        image_filename = None
        
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
        
        post = {
            "title":title,
            "content":content,
            "date":datetime.now(),
            "image": image_filename
        }
        
        blogs_collection.insert_one(post)
        return redirect(url_for('home'))
    
    
# @app.route('/blogs', methods=['GET'])
# def blogs():
#     posts = blogs_collection.find({})
#     posts = [
#         {
#             "_id": str(post["_id"]),
#             "title": post["title"],
#             "content": post["content"],
#             "date": post["date"].strftime("%Y-%m-%d %H:%M:%S") if "date" in post else None
#         }
#         for post in posts
#     ]
#     return render_template('blogs.html', posts=posts)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users_collection.find_one({"email":email})
        
        if user:
            if user['password'] == password:
                session['user'] = user['username']
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials')
                return redirect(url_for('login'))
        
        new_user = {
            "username":username,
            "email":email,
            "password":password
        }
        
        # if users_collection.find_one({"email":email}):
        #     flash('User already exists')
        #     return redirect(url_for('login'))

        users_collection.insert_one(new_user)
        session['user'] = username
        return redirect(url_for('home'))
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

    
if __name__ == "__main__":
    app.run(debug=True, port = 5004)