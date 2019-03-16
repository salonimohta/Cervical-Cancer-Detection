import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, send_file
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddPatient
from flaskblog.models import User, Patient
from flask_login import login_user, current_user, logout_user, login_required
import numpy as np
from flaskblog.utils.losses import *
from flaskblog.utils.preprocess import *
from keras.models import load_model

def predict(T1_path,FLAIR_path,IR_path,label):
    model = load_model("flaskblog/weights/label"+str(label)+"/best.h5",custom_objects={'dice_coefficient': dice_coefficient, 'dice_loss':  dice_loss})
    if label in [1,3,5]:
        T1 = get_data_with_skull_scraping(T1_path)
        if label == 5:
            X = np.array((T1>=10) & (T1<110)).astype(np.uint8)[None,None,...]
        elif label == 3:
            X = np.array(T1>=150).astype(np.uint8)[None,None,...]
        else:
            X = np.array((T1>=80) & (T1<160)).astype(np.uint8)[None,None,...]
        y_pred = model.predict(X)
    else:
        T1 = histeq(to_uint8(get_data_with_skull_scraping(T1_path)))[None,None,...]
        IR = IR_to_uint8(get_data(IR_path))[None,None,...]
        FLAIR = to_uint8(get_data(FLAIR_path))[None,None,...]
        y_pred = model.predict([T1,FLAIR,IR])
    return y_pred.squeeze()


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


def save_file_T1(form_picture,last_name, first_name):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = last_name + first_name + ".nii.gz"
    picture_path = os.path.join(app.root_path, 'static/mri/T1', picture_fn)
    f = request.files.getlist('file_T1')[0]
    f.save(picture_path)
    return picture_fn

def save_file_FLAIR(form_picture,last_name, first_name):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = last_name + first_name + ".nii.gz"
    picture_path = os.path.join(app.root_path, 'static/mri/FLAIR', picture_fn)
    f = request.files.getlist('file_FLAIR')[0]
    f.save(picture_path)
    return picture_fn


def save_file_IR(form_picture,last_name, first_name):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = last_name + first_name + ".nii.gz"
    picture_path = os.path.join(app.root_path, 'static/mri/IR', picture_fn)
    f = request.files.getlist('file_IR')[0]
    f.save(picture_path)
    return picture_fn


def save_file_y_True(form_picture,last_name, first_name):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = last_name + first_name + ".nii.gz"
    picture_path = os.path.join(app.root_path, 'static/mri/y_True', picture_fn)
    f = request.files.getlist('file_y_True')[0]
    f.save(picture_path)
    return picture_fn

@app.route("/addPatient", methods=['GET', 'POST'])
@login_required
def addPatient():
    form = AddPatient()
    if form.validate_on_submit():
        picture_fn_T1 = save_file_T1(form.file_T1.data, form.lastName.data, form.firstName.data)
        picture_fn_FLAIR = save_file_FLAIR(form.file_FLAIR.data, form.lastName.data, form.firstName.data)
        picture_fn_IR = save_file_IR(form.file_IR.data, form.lastName.data, form.firstName.data)
        picture_fn_y_True = save_file_y_True(form.file_y_True.data, form.lastName.data, form.firstName.data)
        patient = Patient(first_name=form.firstName.data, last_name=form.lastName.data, age=form.age.data,
                          gender=form.gender.data, file_t1=picture_fn_T1, file_flair=picture_fn_FLAIR,
                          file_ir=picture_fn_IR, file_y_true=picture_fn_y_True, author=current_user)
        db.session.add(patient)
        db.session.commit()
        flash('Patient information is successfully entered', 'success')
        return redirect(url_for('home'))
    return render_template('addPatient.html', title='Add Patient', form=form)


@app.route("/viewPatient")
@login_required
def viewPatient():
    patient = current_user.patient
    return render_template('viewPatient.html', title='View Patient', patients=patient)


@app.route("/patient/<int:patient_id>")
@login_required
def patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient.html', title='Patient', patient=patient)


@app.route("/downloadfile/t1/<string:path>")
def DownloadFileT1 (path = None):
    if path is None:
        self.Error(400)
    try:
        picture_path = os.path.join(app.root_path, 'static/mri/T1', path)
        return send_file(picture_path, as_attachment=True)
    except Exception as e:
        self.log.exception(e)
        self.Error(400)

@app.route("/downloadfile/flair/<string:path>")
def DownloadFileFLAIR (path = None):
    if path is None:
        self.Error(400)
    try:
        picture_path = os.path.join(app.root_path, 'static/mri/FLAIR', path)
        return send_file(picture_path, as_attachment=True)
    except Exception as e:
        self.log.exception(e)
        self.Error(400)

@app.route("/downloadfile/ir/<string:path>")
def DownloadFileIR (path = None):
    if path is None:
        self.Error(400)
    try:
        picture_path = os.path.join(app.root_path, 'static/mri/IR', path)
        return send_file(picture_path, as_attachment=True)
    except Exception as e:
        self.log.exception(e)
        self.Error(400)


@app.route("/downloadfile/y_True/<string:path>")
def DownloadFileYTrue (path = None):
    if path is None:
        self.Error(400)
    try:
        picture_path = os.path.join(app.root_path, 'static/mri/y_True', path)
        return send_file(picture_path, as_attachment=True)
    except Exception as e:
        self.log.exception(e)
        self.Error(400)


# pragma table_info(patient)

t1_path_base = "flaskblog/static/mri/T1/"
flair_path_base = "flaskblog/static/mri/FLAIR/"
ir_path_base = "flaskblog/static/mri/IR/"
y_true_base = "flaskblog/static/mri/y_True/"
y_pred_base = "flaskblog/static/mri/y_Pred/"


def practice(z_index, class_index, filename):
    path_pred = 'flaskblog/static/mri/y_Pred/'+class_index+'_my_' + z_index + '.png'
    path_true = 'flaskblog/static/mri/y_True/'+class_index+'_my_' + z_index + '.png'
    x = np.load(y_pred_base+str(class_index)+".npy")
    z = np.array(x[:,:,int(z_index)]>0.5).astype(np.uint8())
    img = Image.fromarray(np.uint8(z*255),'L')
    img.save(path_pred)
    x = np.load("flaskblog/static/mri/y_True/"+filename+".npy")
    if class_index !=0:
    	x = np.array(x==int(class_index)).astype(np.uint8()).squeeze()
    z = x[:,:,int(z_index)]
    img = Image.fromarray(np.uint8(z*255),'L')
    img.save(path_true)


@app.route("/analysis/<string:filename>", methods=['GET', 'POST'])
def analysis(filename=None):
    z_index = 0
    file = 1
    if request.method == 'POST':
        if request.form.get('files_dropdown'):
            file = request.form.get('files_dropdown')
        if request.form["SlideNo"]:
            z_index = request.form["SlideNo"]

        practice(z_index, file, filename)
    else:
        y_pred = []
        THRESHOLD = 0.5
        for i in range(1,9):
            y_ = predict(t1_path_base+filename+".nii.gz",flair_path_base+filename+".nii.gz",ir_path_base+filename+".nii.gz",i)
            y_pred.append(y_)
            np.save(y_pred_base+str(i)+".npy",y_)
        y_1 = np.array(y_pred[0] > THRESHOLD)*1
        y_2 = np.array(y_pred[1] > THRESHOLD)*2
        y_3 = np.array(y_pred[2] > THRESHOLD)*3
        y_4 = np.array(y_pred[3] > THRESHOLD)*4
        y_5 = np.array(y_pred[4] > THRESHOLD)*5
        y_6 = np.array(y_pred[5] > THRESHOLD)*6
        y_7 = np.array(y_pred[6] > THRESHOLD)*7
        y_8 = np.array(y_pred[7] > THRESHOLD)*8
        idx = []
        idx.append(np.array(np.where(y_1 == 1)))
        idx.append(np.array(np.where(y_2 == 2)))
        idx.append(np.array(np.where(y_3 == 3)))
        idx.append(np.array(np.where(y_4 == 4)))
        idx.append(np.array(np.where(y_5 == 5)))
        idx.append(np.array(np.where(y_6 == 6)))
        idx.append(np.array(np.where(y_7 == 7)))
        idx.append(np.array(np.where(y_8 == 8)))
        y_final = np.zeros([240,240,48],dtype='int')
        for i in range(8):
            for j in range(idx[i].shape[1]):
                x = idx[i][0][j]
                y = idx[i][1][j]
                z = idx[i][2][j]
                y_final[x][y][z] = i+1
        np.save(y_pred_base+str(0)+".npy",y_final)
        np.save("flaskblog/static/mri/y_True/"+filename+".npy",get_data(y_true_base+filename+".nii.gz"))
        # return redirect(url_for('analysis'), z_index = z_index)
    return render_template('analysis.html', z_index = z_index, file=file)