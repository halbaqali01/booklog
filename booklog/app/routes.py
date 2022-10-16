from flask import render_template, flash, redirect, url_for, request 
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, BookRegistrationForm, BookEditForm, BorrowForm, BorrowEditForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Post, Book, Borrow, load_all_users
from datetime import datetime

# Records when user was last seen
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Contents Page Route & Definition Link
@app.route('/contents')
@login_required
def contents():
    #Shows List of Features & Links to Them - Very Simple
    return render_template('contents.html', title='Contents')

# Home Page Route & Definition Link
@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    borrows = Borrow.query.all()

    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('home'))
    
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('home', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('home', page=posts.prev_num) if posts.has_prev else None

    return render_template('home.html', title='Home Page', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, borrows=borrows)

# User Explore Route
@app.route('/explore')
@login_required
def explore():
    borrows = Borrow.query.all()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('home.html', title='Explore',posts=posts.items, next_url=next_url, prev_url=prev_url, borrows=borrows)

# User Profile View Function
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    users = User.query.all()

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username,page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username,page=posts.prev_num) if posts.has_prev else None

    form = EmptyForm()
    return render_template('profile.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form, users=users)

# Profile Edit Route
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

# Login Page Route & Definition Link
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is user.admin:
            flash('Admin Login Successful')
            return redirect(url_for('admin_home'))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title= 'Sign In', form=form)

# Logout Route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Register User Route & Definition Link
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html', title="Register", form=form)

# Follow a User
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('home'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('home'))

# Unfollow a User
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('home'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:    
        return redirect(url_for('home'))

# Penalties Page Route & Definition Link
@app.route('/penalties')
@login_required
def penalties():
    #Shows list of Penalties & potentially how many penalties does user have
    return render_template('penalties.html', title='Penalties')

# Book List Route & Definition Link
@app.route('/booklist')
@login_required
def booklist():
    books = Book.query.all()
    borrows = Borrow.query.all()
    return render_template('booklist.html', title='Book List', books=books, borrows=borrows)

# Post Edit Route
@app.route('/posts/<id>', methods=['GET','POST'])
@login_required
def update_posts(id):
    form = PostForm()
    post = Post.query.get(id)

    if post.author == current_user or current_user.is_admin:
        if form.validate_on_submit(): 
            post.body = form.post.data 
            db.session.commit() 
            flash('Your changes have been saved.') 
            return redirect(url_for('home')) 
        elif request.method == 'GET': 
            form.post.data = post.body 
        return render_template('edit_post.html', title='Edit Post', form=form) 
    return redirect(url_for('home')) 

# Delete Posts Route
@app.route('/delete_posts/<id>', methods=['GET','POST'])
@login_required
def delete_posts(id):
    post = Post.query.get(id)

    if post.author == current_user or current_user.is_admin:
        db.session.delete(post) 
        db.session.commit() 
        flash('The post has been deleted!') 
        return redirect(url_for('home')) 
    return render_template('home.html', title='Delete Post') 

# Book Request Form
@app.route('/borrow', methods=['GET','POST'])
@login_required
def borrow():
    form = BorrowForm()
    if form.validate_on_submit():
        borrow = Borrow(book=form.book.data, user=current_user)
        db.session.add(borrow)
        db.session.commit()
        flash('Your request has been sent')
        return redirect(url_for('booklist'))
    
    return render_template('borrow_form.html', title='Borrow Page', form=form)


# Admin Related Routes
# Home Page Route & Definition Link
@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    users = load_all_users()
    books = Book.query.all()
    borrows = Borrow.query.all()

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username,page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username,page=posts.prev_num) if posts.has_prev else None

    return render_template('admin_home.html', title='Home Page', users=users, books=books, posts=posts.items, next_url=next_url, prev_url=prev_url, borrows=borrows)

# Add User Route
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = RegistrationForm()
    if current_user.is_admin:
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, the user has been registered!')
            return redirect(url_for('admin'))
        return render_template('add_user.html', title="Register", form=form)
    return redirect(url_for('admin'))

# Delete User Route
@app.route('/delete_user/<id>', methods=['GET','POST'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if current_user.is_admin:
        db.session.delete(user) 
        db.session.commit() 
        flash('The user has been deleted!') 
        return redirect(url_for('admin')) 
    return render_template('home.html', title='Delete User')

# Register Books
@app.route('/registerbook', methods=['GET', 'POST'])
@login_required
def register_book():
    form = BookRegistrationForm()
    if current_user.is_admin:
        if form.validate_on_submit():
            book = Book(book=form.book.data, author=form.author.data, type=form.type.data, availibility = form.availibility.data)
            db.session.add(book)
            db.session.commit()
            flash('Congratulations, you have added a book!')
            return redirect(url_for('admin'))
    return render_template('register_book.html', title="Register Book", form=form)

# Book Edit Route
@app.route('/book/<id>', methods=['GET','POST'])
@login_required
def edit_book(id):
    form = BookEditForm()
    book = Book.query.get(id)

    if current_user.is_admin:
        if form.validate_on_submit(): 
            book.book = form.book.data
            book.author = form.author.data
            book.type = form.type.data  
            book.availibility = form.availibility.data 
            db.session.commit() 
            flash('Your changes have been saved.') 
            return redirect(url_for('admin')) 
        return render_template('edit_book.html', title='Edit Book', form=form) 
    return redirect(url_for('admin'))

# Delete Book Route
@app.route('/delete_book/<id>', methods=['GET','POST'])
@login_required
def delete_book(id):
    books = Book.query.get(id)
    if current_user.is_admin:
        db.session.delete(books) 
        db.session.commit() 
        flash('The book has been deleted!') 
        return redirect(url_for('admin')) 
    return render_template('admin_home.html', title='Delete Book')

# Edit Loan Route
@app.route('/borrow/<id>', methods=['GET','POST'])
@login_required
def edit_borrow(id):
    form = BorrowEditForm()
    borrow = Borrow.query.get(id)

    if current_user.is_admin:
        if form.validate_on_submit(): 
            borrow.book = form.book.data
            borrow.author = form.user.data
            db.session.commit() 
            flash('Your changes have been saved.') 
            return redirect(url_for('admin')) 
        return render_template('edit_borrow.html', title='Edit Loan', form=form) 
    return redirect(url_for('admin'))

# Delete Loan Route
@app.route('/delete_borrow/<id>', methods=['GET','POST'])
@login_required
def delete_borrow(id):
    borrow = Borrow.query.get(id)
    if current_user.is_admin:
        db.session.delete(borrow) 
        db.session.commit() 
        flash('The loan has been deleted!') 
        return redirect(url_for('admin')) 
    return render_template('admin_home.html', title='Delete Book')
