from flask import Flask ,redirect, url_for, render_template, request, flash
from flask_login import LoginManager,UserMixin,login_user, logout_user, login_required,current_user
from flask_sqlalchemy import SQLAlchemy
import flask_whooshalchemy as wa
from whoosh.analysis import StemmingAnalyzer
import os
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


# con = sqlite3.connect('./tmp/database.db')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/database.db'
app.config['SECRET_KEY'] = 'JIHDGJIDHFHJDFJ'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =True
app.config['WHOOSH_BASE']='whoosh'

ALLOWED_EXTENSIONS = set(['png','gif','jpg','jpeg'])

db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view ='login'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
       


class BlogPost(db.Model,UserMixin):
       __tablename__ = 'bloggingposts'
       __searchable__  = ['author','title','sub_title','content'] # indexed fields
       __analyzer__ = StemmingAnalyzer()
       id = db.Column(db.Integer,primary_key=True)
       author = db.Column(db.String(255))
       title = db.Column(db.String(255))
       sub_title = db.Column(db.String(255))
       content = db.Column(db.Text)
       blog_pix =db.Column(db.String(200))
       author_id = db.Column(db.Integer)
       total_view = db.Column(db.BigInteger,default=0)
       today=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
      #   date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)





class User(db.Model,UserMixin):
       id = db.Column(db.Integer,primary_key=True)
       username = db.Column(db.String(100))
       name = db.Column(db.String(100))
       password = db.Column(db.String(50))
       email = db.Column(db.String(255))
       career = db.Column(db.String(255))
       fblk = db.Column(db.String(255))
       twlk = db.Column(db.String(255))
       anylk = db.Column(db.String(255))
       dob = db.Column(db.String(50))
       address = db.Column(db.String(255))
       user_pix =db.Column(db.String(200))
       message = db.Column(db.Text)
       today=db.Column(db.Date, nullable=False, default=datetime.now)


# class srcpost(db.Model):
#       _searchable_ = ['author','title','sub_title','content','blog_pix']

# wa.whoosh_index(app,srcpost)

# @app.route('/search')
# def search():
#        posts=BlogPost.query.whoosh_search(request.args.get('query')).all()

#        return render_template('index.html', posts=posts)






@app.route('/')
@app.route('/home')
def index():
   page = request.args.get('page', 1, type = int)
   posts = BlogPost.query.order_by(BlogPost.today.desc()).paginate(page=page, per_page=5)
   # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
   return render_template('index.html',posts=posts)

# wa.whoosh_create(app, BlogPost)

@app.route('/searching')
def searching():
   posts = BlogPost.query.whoosh_search(request.args.get('query')).all()
   return render_template('index.html', posts = posts)



@app.route('/post/<int:id>')
def post(id):
       content = BlogPost.query.filter_by(id=id).first()
       content.total_view +=1
       db.session.commit()
       #_content = posts = BlogPost.query.all()
       return render_template('./post.html',content1=content)


@login_manager.user_loader
def load_user(user_id):
       return User.query.filter_by(id=user_id).first()




@app.route('/register', methods=['GET','POST'])
def reg():
   if request.method =='POST':
      username = request.form['username']
      name = request.form['name']
      email = request.form['email']
      message = request.form['message']
      password = request.form['password']
      career = request.form['career']
      dob = request.form['dob']
      fblk = request.form['fblk']
      twlk = request.form['twlk']
      anylk = request.form['anylk']
      address = request.form['address']
      user_pix = request.files['user_pix']
      if user_pix and allowed_file(user_pix.filename):
         filename=secure_filename(user_pix.filename)
         user_pix.save(os.path.join('./static/userpix',filename))
         url = str(filename)
         new_reg = User(username=username,fblk=fblk, twlk=twlk, anylk=anylk,name=name,email=email,message=message, password= password,career=career, dob =dob, address =address,user_pix =url)
         db.session.add(new_reg)
         db.session.commit()
         flash("Registed")
         return redirect(url_for('login'))
      else:
         flash("invalid pictures") 
         return redirect(url_for('register.html'))


   return render_template('register.html')








@app.route('/about')
def about():
   return render_template('about.html')

@app.route('/contact')
def contact():
   return render_template('contact.html')

"""@app.route('/post')
def post():
   return render_template('post.html')"""


@app.route('/login',methods=['GET','POST'])
def login():
   if request.method == 'POST':
      username=request.form['username']
      password=request.form['password']
      user=User.query.filter_by(username=username).first()
      if user:
         if user.password == password:
            login_user(user) #save session
            return redirect(url_for('dashboard'))
         else:
            return'invalid password'
      else:
         return 'inavlid username'


   return render_template('login.html')





@app.route('/contact',methods=['POST'])
def content():
   authors = request.form['author']
   titles = request.form['title']
   sub_titles = request.form['sub_title']
   contents = request.form['content']
   #todays = request.form['today']
   new_post = BlogPost(author=authors,title=titles,content=contents,sub_title=sub_titles)
   db.session.add(new_post)
   db.session.commit()
   
   return render_template('contact.html')




# @app.route('/profile_view/<int:id>')
# def profile_view(id):
#        profile_views = User.query.filter_by(id=id).first()
#        admin_post = BlogPost.query.filter_by(author_id=id).all()
#        #_content = posts = BlogPost.query.all()
#        return render_template('./profile/profile_view.html',profile_views=profile_views,admin_post=admin_post)



@app.route('/useradminprofile/<int:id>')
def useradminprofile(id):
       profile_views = User.query.filter_by(id=id).first()
       admin_post = BlogPost.query.filter_by(author_id=id).all()
       return render_template('./useradminprofile/useradminprofile.html',profile_views=profile_views,admin_post=admin_post)
       


"""@app.route('/delete/<int:id>')
def drop(id):
       blog_content = BlogPost.query.filter_by(id=id).delete()
       db.session.commit()
       return 'deleted'
"""
"""@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
       update_blog = BlogPost.query.filter_by(id=id).first()
       if request.method == 'POST':
              title = request.form['title']
              content = request.form['content']
              update_blog.title = title
              update_blog.content = content
              db.session.commit()
              return 'updated'
       return render_template('./updates.html',update_blog=update_blog)"""

@app.route('/dashboard')
@login_required
def dashboard():
   posts = BlogPost.query.order_by(BlogPost.today.desc()).all()
   return render_template('./dashboard/starter.html',posts=posts)


@app.route('/about-us')
@login_required
def profile():
        posts = User.query.all()
        return render_template('./profile/about-us.html', posts=posts)


@app.route('/create_post', methods=['GET','POST'])
@login_required
def create_post():
   posts = User.query.all()
   if request.method =='POST':
      authors = request.form['author']
      titles = request.form['title']
      sub_titles = request.form['sub_title']
      contents = request.form['content']
      #author_id = request.form['current_user.id']
      blog_pix = request.files['blog_pix']
      if blog_pix and allowed_file(blog_pix.filename):
         filename=secure_filename(blog_pix.filename)
         blog_pix.save(os.path.join('./static/blogpix',filename))
         url = str(filename)
         new_post = BlogPost(author=authors,title=titles,content=contents,sub_title=sub_titles,blog_pix=url,author_id=current_user.id)
         db.session.add(new_post)
         db.session.commit()
         flash("Blog has been posted")
         return redirect(url_for('create_post'))
      else:
         flash("invalid pictures")
         return redirect(url_for('create_post'))

      
   return render_template('./dashboard/create_post.html', posts=posts)



@app.route('/editt/<int:id>')
def postt(id):
       content = BlogPost.query.filter_by(id=id).first()
       #_content = posts = BlogPost.query.all()
       return render_template('./dashboard/update.html',content=content)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
       update_blog = BlogPost.query.filter_by(id=id).first()
       if request.method == 'POST':
              title = request.form['title']
              content = request.form['content']
              author = request.form['author']
              sub_title = request.form['sub_title']
              update_blog.title = title
              update_blog.content = content
              update_blog.author = author
              update_blog.sub_title = sub_title
              db.session.commit()
              return 'updated'

       return render_template('./dashboard/update.html',update_blog=update_blog)


@app.route('/delete/<int:id>')
def drop(id):
       blog_content = BlogPost.query.filter_by(id=id).delete()
       db.session.commit()
       return 'deleted'

@app.route('/logout')
def logout():
       logout_user()
       
       return redirect(url_for('login'))

if __name__ == "__main__":
   # manager.run()
    app.run(debug=True, port=7000)
