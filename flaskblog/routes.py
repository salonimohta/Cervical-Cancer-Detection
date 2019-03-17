from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,AddPatient
from flaskblog.models import User,Patient
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flaskblog.token import generate_confirmation_token, confirm_token
from ww import f
import os
from werkzeug.datastructures import FileStorage
from random import *
import csv

# File = open('out.csv')
# Reader = csv.reader(File)
# Data = list(Reader)

csv_reader = csv.reader('out.csv',delimiter=',')


s=URLSafeTimedSerializer('Thisisasecret!')


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html',title='About')

@app.route('/causes')
def causes():
    return render_template('causes.html',title='Causes of Cervical cancer')

@app.route('/symptoms')
def symptoms():
    return render_template('symptoms.html',title='News about Cervical cancer')


@app.route('/risk_prone')
def risk_prone():
    return render_template('risk_prone.html',title='Risk Prone Areas')

@app.route('/news')
def news():
    return render_template('news.html',title='news')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        send_email(user.email,confirm_url=confirm_url)

        flash('A confirmation email has been sent to your mail. Please verify your email', 'success')
        return redirect('register')
        if current_user.confirmed:
            login_user(user)
            return redirect('home')
        flash('Please confirm your account!', 'warning')
        return render_template('unconfirmed.html')
    return render_template('register.html',title='register',form=form)

@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('home'))


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
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
    form = RequestResetForm()
    return render_template('account.html', title='Account',form=form)

def send_email(email,confirm_url):
    msg = Message('Please confirm your email',sender='noreply.ccd@gmail.com',recipients=[email])
    msg.body='''Welcome! Thanks for signing up. Please follow this link to activate your account:
{}. 
Cheers!
    '''.format(confirm_url)
    mail.send(msg)

@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('home')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')


def send_reset_email(user):
    token = user.get_reset_token()
    msg=Message('Password Reset Request',sender='noreply.ccd@gmail.com',recipients=[user.email])
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
        flash('Your password has been updated! You are now able to log in!','success')
        return redirect(url_for("login"))
    return render_template('reset_token.html',title='Reset Password',form=form)

@app.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    send_email(current_user.email, confirm_url)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))

def save_file(form_picture,last_name, first_name):
    _, f_ext = os.path.splitext(form_picture.filename)
    f = FileStorage(form_picture.filename)
    #picture_fn = last_name + first_name + ".jpg"
    picture_fn = f.filename
    picture_path = os.path.join(app.root_path, 'static\cervix', 'picture_fn')
    f = request.files.getlist('file')[0]
    f.save(picture_path)
    return picture_fn

def reading(x):
    for row in csv_reader:
        if row[2] == x:
            return row[1]
            break


def send_mail(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender='noreply.ccd@gmail.com'
    )
    mail.send(msg)

@app.route("/detect", methods=['GET', 'POST'])
@login_required
def detect():
    form = AddPatient()
    if form.validate_on_submit():
        picture_fn = save_file(form.file.data, form.lastName.data, form.firstName.data)
        patient = Patient(first_name=form.firstName.data, last_name=form.lastName.data, age=form.age.data,
                          gender=form.gender.data,latitude=form.latitude.data,longitude=form.longitude.data, file=picture_fn, author=current_user)
        db.session.add(patient)
        db.session.commit()
        flash('Patient information is successfully entered', 'success')
        x =0
        #x= reading(picture_fn)
        x=randint(0,2)
        send_mail(current_user.email,'Results of Cervical Cancer',render_template('add.html',x=x ))
    return render_template('detect.html', title='Detect Cancer', form=form)


