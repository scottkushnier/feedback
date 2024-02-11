"""Flask app for Cupcakes"""
from models import db, connect_db, User, Feedback
from flask import Flask, redirect, render_template, request, session
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'fango'
connect_db(app)

bcrypt = Bcrypt()


@app.route('/')
def home_page():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if ('username' in request.form):           # POST
        username = request.form['username']
        password = request.form['password']
        hash_password = bcrypt.generate_password_hash(password)
        hash_password_str = hash_password.decode('utf8')
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        user = User(username=username, password=hash_password_str, email=email,
                    first_name=firstname, last_name=lastname)
        db.session.add(user)
        db.session.commit()
        session['userid'] = user.username
        return redirect(f'/users/{user.username}')
    return render_template('register.html')        # GET


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if ('username' in request.form):               # POST
        print('still have username: ', request.form['username'])
        username = request.form['username']
        password = request.form['password']
        user = User.query.get(username)
        if (not user):
            return render_template('login.html', username=username, bad_user=True)
        if (bcrypt.check_password_hash(user.password, password)):
            session['userid'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            return render_template('login.html', username=username, bad_password=True)
    if 'userid' in session:             # GET, if already logged in, go to feedback
        username = session['userid']
        return redirect(f'/users/{username}')
    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout_page():
    session.pop('userid')
    return redirect('/login')


def validate_user(username):
    if ('userid' in session):
        if (session['userid'] == username):
            return True
        else:
            return False
    else:
        return False


@app.route('/users/<string:username>')
def user_page(username):
    if (validate_user(username)):
        feedbacks = Feedback.query.filter_by(username=username).all()
        return render_template('/feedback.html', feedbacks=feedbacks, username=username)
    else:
        return redirect('/login')


@app.route('/users/<string:username>/delete_conf', methods=['POST'])
def user_unregister_confirm(username):
    if (validate_user(username)):
        feedbacks = Feedback.query.filter_by(username=username).all()
        return render_template('/feedback.html', feedbacks=feedbacks, username=username, confirm_unregister=True)
    else:
        return redirect('/login')


@app.route('/users/<string:username>/delete', methods=['POST'])
def user_unregister(username):
    if (validate_user(username)):
        Feedback.query.filter_by(username=username).delete()
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('userid')
    return redirect('/login')


@app.route('/users/<string:username>/feedback/add')
def user_add_feedback(username):
    if (validate_user(username)):
        return render_template('/feedback-add.html')
    else:
        return redirect('/login')


@app.route('/users/<string:username>/feedback/add', methods=['POST'])
def user_add_feedback_post(username):
    title = request.form['title']
    content = request.form['content']
    print(title, content)
    feedback = Feedback(title=title, content=content, username=username)
    db.session.add(feedback)
    db.session.commit()
    return redirect(f'/users/{username}')


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{username}')


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    if ('title' in request.form):
        feedback = Feedback.query.get_or_404(feedback_id)
        title = request.form['title']
        content = request.form['content']
        feedback.title = title
        feedback.content = content
        db.session.add(feedback)
        db.session.commit()
        username = feedback.username
        return redirect(f'/users/{username}')
    else:
        feedback = Feedback.query.get_or_404(feedback_id)
        username = feedback.username
        if (validate_user(username)):

            title = feedback.title
            content = feedback.content
            return render_template('/feedback-edit.html', title=title, content=content)
        else:
            return redirect('/login')
