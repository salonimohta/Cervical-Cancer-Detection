from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from ww import f

s=URLSafeTimedSerializer('Thisisasecret!')

posts=[
    {
        'author': 'Saloni Mohta',
        'title': 'Blog post 1',
        'content': ' First post content',
        'date_posted': 'March 12, 2019'
    },
    {
        'author': 'Inolas Athom',
        'title': 'Blog post 2',
        'content': 'Second post content',
        'date_posted' : 'March 13, 2019'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html',posts=posts)

@app.route('/about')
def about():
    return render_template('about.html',title='About')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        token=s.dumps(form.email.data,salt='confirm-email')
        msg=Message('Confirm Email', sender='somebeek@gmail.com',recipients=[form.email.data])
        link=url_for('confirm_email',token=token,_external=True)
        msg.body='Click on this link to confirm your email {}'.format(link)
        mail.send(msg)

        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("home"))

    return render_template('register.html',title='register',form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email=s.loads(token,salt='confirm-email',max_age=60)
    except SignatureExpired:
        flash('The token is either invalid or expired')
        return redirect(url_for(''))

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Unsuccessful Log In. Please check username and password again','danger')
    return render_template('login.html',title='login',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

def send_reset_email(user):
    token = user.get_reset_token()
    msg=Message('Password Reset Request',sender='somebeek@gmail.com',recipients=[user.email])
    msg.body='''To reset your password visit the following link:
{}

If you did not make this request then simply ignore this email and no changes will be made.
    
'''.format(url_for('reset_token',token=token,_external=True))
    mail.send(msg)

@app.route('/reset_password',methods=['GET','POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('request_reset.html',title='Reset Password', form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('The token is either invalid or expired')
        return redirect(url_for('request_reset'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Your password has been updated! You are nowable to log in!','success')
        return redirect(url_for("login"))
    return render_template('reset_token.html',title='Reset Password',form=form)


