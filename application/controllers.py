from flask import Flask, request, flash, redirect, url_for, session, jsonify, Response, json
from flask import render_template
from flask import current_app as app
from datetime import timedelta, datetime
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse,urljoin
from application.database import db
from sqlalchemy import or_
from application.models import User
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from application.models import *
from application.forms import *

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.context_processor
def search_global():
    search_form=SearchForm()
    return dict(search_form=search_form)

@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm() 
    forgot_form = ForgotForm()   
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()        
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                session['username']=form.username.data
                return redirect(url_for('dashboard',username=user.username))
            else:
                flash("Wrong Password - Try Again!","warning")
        else:
            flash("The User Doesn't Exist! Try Again...","warning")
    return render_template("login.html",form=form,forgot_form=forgot_form)

@app.route("/reset", methods=["GET","POST"])
def reset():  
    form =ForgotForm()    
    formid = request.args.get('formid',1, type=int) 
    print(formid)
    if request.method=='POST' and formid==1:
        user = User.query.filter_by(email=form.email.data).first()
        if user: 
            if user.dob==form.dob.data:
                return redirect(url_for('reset_password',username=user.username))
            else:
                flash("Date of Birth doesn't match", "warning")
        else:
            flash("Email ID doesnt match from the record","warning")

    if request.method=='POST' and formid==2:
        user = User.query.filter_by(email=form.email.data).first()
        if user: 
            if user.dob==form.dob.data:
                flash("Username is: " + user.username,"success")
                return redirect(url_for('login'))
            else:
                flash("Date of Birth doesn't match", "warning")
        else:
            flash("Email ID doesnt match from the record","warning")        
    return render_template("reset_password.html",form=form,type=formid)

@app.route("/reset_password/<string:username>", methods=["GET","POST"])
def reset_password(username):
    form = ChangePasswordForm() 
    if request.method=="POST":
        hashed_pw = generate_password_hash(form.confirm_password.data, "sha256")
        try:
            db.session.query(User).where(User.username==username).update({User.password : hashed_pw},synchronize_session=False)
            db.session.commit() 
            flash("Password reset succussfully!!!","success")
            return redirect(url_for('login'))   
        except:
            db.session.rollback()
            flash("Password Update Failed. Try Again !","warning")      
    return render_template('reset_password_user.html',form=form,username=username)                      


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()     
    if form.validate_on_submit():       
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            if form.profile_pic.data is None:
                dest_path = "../static/Images/default_dp.png"
            else:
                img = form.profile_pic.data
                dest_path=f'static/Uploads/{img.filename}'
                img.save(dest_path)
                dest_path=f'../static/Uploads/{img.filename}'

            user = User(username=form.username.data.lower(), fname=form.fname.data, lname=form.lname.data,profession=form.profession.data,
                            image=dest_path,password=hashed_pw, email=form.email.data.lower(), location=form.location.data, dob=form.dob.data)
            
            try:
                db.session.add(user)
                db.session.commit()
            except:
                db.session.rollback() 
                flash('Database insertion failed. Try Again !','warning')   

            flash('Congratulations, you are now a registered user!','success')
            return redirect(url_for('login'))

    # if form.errors:
    #     for i in form.errors:
    #         flash(form.errors[i][0])
    return render_template('register.html', form=form)

@app.route("/dashboard/<string:username>", methods=['GET', 'POST'])
@login_required
def dashboard(username):
    if request.method=="GET" and session['username']==username:
        form = CommentForm()
        comment = Comment.query.all()    
        user = User.query.all()
        like = Like.query.all()
        blog = current_user.followed_posts().order_by(Blog.date_created.desc()).all()
        total_followers = current_user.followers.filter_by(followed_id=current_user.user_id).all()
        total_following = current_user.followed.filter_by(follower_id=current_user.user_id).all()
        return render_template('dashboard.html',blog=blog, form=form, comment=comment, user=user,like=like,
                             total_followers=total_followers, total_following=total_following, date=datetime.now())  
    else:
        return redirect(url_for('login'))

@app.route("/profile/<string:username>", methods=['GET'])
def profile(username):
    if request.method=="GET":
        all_user = User.query.all()
        user = User.query.filter_by(username=username).first()
        blog = Blog.query.filter_by(user_id=user.user_id).order_by(Blog.date_created.desc()).all()
        form = CommentForm()
        comment = Comment.query.all() 
        total_followers = user.followers.filter_by(followed_id=user.user_id).all()
        total_following = user.followed.filter_by(follower_id=user.user_id).all()   
        return render_template('user_profile.html',blog=blog, form=form, comment=comment, user=user, all_user=all_user,
            total_followers=total_followers, total_following=total_following, date=datetime.now())  


@app.route("/delete_profile/<string:username>", methods=['GET', 'POST'])
@login_required
def delete_profile(username):
    if request.method=="GET" and session['username']==username:
        user = User.query.filter_by(username=username).first()
        try:
            db.session.delete(user)
            db.session.commit()
            flash('Profile deleted successfully','success')  
        except:
            flash('There was a problem deleting user, try again...','error')    
        return redirect(url_for('logout'))


@app.route("/edit_profile/<string:username>", methods=['GET', 'POST']) 
@login_required   
def edit_profile(username):
    form1 = EditProfileForm()
    form2 = ChangePasswordForm()
    form3 = ChangePicForm()

    formid = request.args.get('formid',1, type=int)     
    if form1.validate_on_submit() and session['username']==username and formid==1:
        current_user.username = form1.username.data
        current_user.fname = form1.fname.data
        current_user.lname = form1.lname.data
        current_user.profession = form1.profession.data
        current_user.location = form1.location.data
        current_user.email = form1.email.data
        current_user.mobile = form1.mobile.data
        current_user.dob = form1.dob.data
        try:
            db.session.add(current_user)
            db.session.commit()
            flash("Changes Saved Succussfully!!!",'success')
        except IntegrityError:
            db.session.rollback()
            flash("Email ID already exists !!!",'warning')     
        except:
            db.session.rollback()
            flash("Database Update Failed. Try Again !",'error')               
        return redirect(url_for('dashboard',username=current_user.username))

    elif form2.validate_on_submit() and session['username']==username and formid==2:

        if check_password_hash(current_user.password, form2.current_password.data):
            if form2.new_password.data == form2.confirm_password.data:
                hashed_pw = generate_password_hash(form2.confirm_password.data, "sha256")
                try:
                    db.session.query(User).where(User.username==username).update({User.password : hashed_pw},synchronize_session=False)
                    db.session.commit() 
                    flash("Password updated succussfully!!!","success")   
                except:
                    db.session.rollback()
                    flash("Password Update Failed. Try Again !","error")        # revisit for this flash message       
                return redirect(url_for('dashboard',username=current_user.username)) 

    elif form3.validate_on_submit() and session['username']==username and formid==3:
        user = User.query.filter_by(username=current_user.username).first()

        if form3.profile_pic.data is None:
            dest_path = "../static/Images/default_dp.png"
        else:
            img = form3.profile_pic.data
            dest_path=f'static/Uploads/{img.filename}'
            img.save(dest_path)
            dest_path=f'../static/Uploads/{img.filename}'
        
        user.image=dest_path

        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback() 
            flash('Database insertion failed. Try Again !','error')
        return redirect(url_for('dashboard',username=current_user.username))
    return render_template('edit_profile.html',form=form1,form2=form2,form3=form3)

@app.route('/add_post/<string:username>', methods=['GET', 'POST'])
@login_required
def add_post(username):
    form = PostForm()

    if form.validate_on_submit() and session['username']==username:
        user = User.query.filter_by(username=username).first() 
        dest_path = ''
        if form.image.data:
            img = form.image.data
            dest_path=f'static/Uploads/{img.filename}'
            img.save(dest_path)
            dest_path=f'../static/Uploads/{img.filename}'
        post = Blog(title=form.title.data, content=form.content.data, user_id=current_user.user_id, blog_file=dest_path, category=form.category.data, date_created=datetime.now(),user=user)
        try:
            db.session.add(post)
            db.session.commit()
            flash("New post added successfully",'success')
            return redirect(url_for('profile',username=current_user.username))
        except:
            db.session.rollback()
            print('error')
            flash("There was a problem while adding new post. Try Again !", 'warning')
            return render_template('add_post.html',form=form)

    return render_template('add_post.html',form=form)

@app.route('/edit_post/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_post(blog_id): 
    form = EditPostForm()
    blog = Blog.query.filter_by(id=blog_id).first()

    if request.method == 'GET':
        form.title.data = blog.title
        form.category.data = blog.category
        form.content.data = blog.content
        form.image.data = blog.blog_file

    if request.method=='POST' and session['username']==current_user.username:
        blog.title = form.title.data
        blog.content = form.content.data
        blog.category = form.category.data
        
        dest_path = ''
        print(form.image.data)
        if form.image.data and blog.blog_file:
            img = form.image.data
            dest_path=f'static/Uploads/{img.filename}'
            img.save(dest_path)
            dest_path=f'../static/Uploads/{img.filename}'
            blog.blog_file = dest_path
            print(dest_path)
       
        try:
            db.session.add(blog)
            db.session.commit()
            flash("Edit done successfully",'success')
            return redirect(url_for('profile',username=current_user.username))
        except:
            db.session.rollback()
            flash("There was a problem while editting post. Try Again !", 'warning')
            return render_template('edit_post.html',form=form)

    return render_template('edit_post.html',form=form,blog=blog)

@app.route('/delete_post/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def delete_post(blog_id):
    print(blog_id)
    blog = Blog.query.filter_by(id=blog_id).first()
    comment = Comment.query.filter_by(post_id=blog_id).all()
    print(comment)
    like = Like.query.filter_by(post_id=blog_id).all()
    print(like)

    try:
        for i in comment:
            db.session.delete(i)
        for j in like:
            db.session.delete(j)
        db.session.delete(blog)
        db.session.commit()
        flash("Blog deleted successfully", 'success')
    except:
        db.session.rollback()
        flash("There was a problem while deleting post. Try Again !", 'warning')

    return redirect(url_for('profile',username=current_user.username))

@app.route("/like_post/<blog_id>", methods=["GET", "POST"])
@login_required
def like(blog_id):

    blog = Blog.query.filter_by(id=blog_id).first()
    like = Like.query.filter_by(user_id=current_user.user_id, post_id=blog_id).first()
    if not blog:
        return jsonify({'error': 'Post does not exist.'}, 400)

    elif like:
        try:
            db.session.delete(like)   
            db.session.commit()
        except:
            flash('Not able to unlike the post at this moment. Try Again !!!','warning')     

    else:
        try:
            like = Like(user_id=current_user.user_id, post_id=blog_id,blog=blog)        
            db.session.add(like)                
            db.session.commit()
        except:    
            flash('Not able to like the post at this moment. Try Again !!!','warning')       

    return jsonify({"likes": len(blog.likes), "liked": current_user.user_id in map(lambda x: x.user_id, blog.likes)})    

@app.route('/add_comment/<blog_id>', methods=['POST'])
@login_required
def add_comment(blog_id):
    if request.method=='POST':
        c = request.form['comment']
        print(c)
        blog = Blog.query.filter_by(id=blog_id).first() 
        
        comment = Comment(text=c, user_id=current_user.user_id, post_id=blog_id, date_created=datetime.now(), blog=blog)
    
        try:
            db.session.add(comment)         
            db.session.commit()
            return jsonify({'comment':c,'c_id':comment.id,'comment_count':len(blog.comments), 'image':comment.user.image,'username':comment.user.username,'fname':comment.user.fname,'lname':comment.user.lname})                     
        except:
            db.session.rollback()
            print('error')
            flash('There was a problem adding comment, try again...','warning')
    return redirect(url_for('dashboard',username=current_user.username))

@app.route('/delete_comment/<comment_id>', methods=['GET','POST'])
@login_required
def delete_comment(comment_id):  
    
    comment = Comment.query.filter_by(id=comment_id).first() 
    print("comment",comment)
    print(len(comment.blog.comments))
    try:
        db.session.delete(comment)   
  
        db.session.commit()
        total_comment = len(comment.blog.comments) 
        print(total_comment)   
        return jsonify({'comment_count':total_comment})  
                          
    except:
        db.session.rollback()
        print('error')
        flash('There was a problem deleting comment, try again...','warning')
    return redirect(url_for('dashboard',username=current_user.username))

@app.route('/following/<string:username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    # if current_user.followed.filter_by(followed_id=user.user_id).first() is None:
    if user.is_following(user) == False:
        f = Follow(follower=current_user, followed=user, timestamp=datetime.now())
        try:
            db.session.add(f)
            db.session.commit()
        except:
            db.session.rollback()
            flash("Not able to follow at this moment. Try Again","warning")    
    return redirect(url_for('profile',username=current_user.username))   


@app.route('/followers/<string:username>', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    # if current_user.followers.filter_by(follower_id=user.user_id).first() is None:

    if user.is_followed_by(user) == False:
        f = current_user.followed.filter_by(followed_id=user.user_id).first()
        if f:
            try:
                db.session.delete(f)
                db.session.commit()
            except:
                db.session.rollback()
                flash("Not able to unfollow at this moment. Try Again","warning")    
    return redirect(url_for('profile',username=current_user.username)) 

@app.route('/remove_request/<string:username>', methods=['GET', 'POST'])
@login_required
def remove_request(username):
    user = User.query.filter_by(username=username).first()
    print(username)
    if user.is_followed_by(user) == False:
        f = user.followed.filter_by(followed_id=current_user.user_id).first()
        if f:
            try:
                db.session.delete(f)
                db.session.commit()
            except:
                db.session.rollback()
                flash("Not able to remove request at this moment. Try Again","warning")    
    return redirect(url_for('profile',username=current_user.username)) 

@app.route("/search/<username>", methods=["POST"])
@login_required
def search(username):
    search_form=SearchForm()
    if session['username']==username:
        search_user="%{}%".format(search_form.searched.data)
        search_result = User.query.filter(or_(User.username.like(search_user),User.fname.like(search_user),User.lname.like(search_user))).all()
        return render_template('search_result.html',search_result=search_result,user=current_user)
    return redirect(url_for('dashboard',username=current_user.username))    

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    logout_user()
    flash("Logged Out Successfully !!!",'success')
    return redirect(url_for('login')) 

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500    
