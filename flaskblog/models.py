from datetime import datetime
from ww import f
from flaskblog import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader #used to decorate the fn so that the extension knows this the function for user_id
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
    confirmed=db.Column(db.Boolean,nullable=False,default=False)
    password=db.Column(db.String(60),nullable=False)
    patient = db.relationship('Patient', backref='author', lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f("User('{self.username}','{self.email}','{self.image_file}','{self.confirmed}')")


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    age = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(6), nullable=True)
    latitude = db.Column(db.String(20),nullable=True)
    longitude= db.Column(db.String(20), nullable=True)
    file = db.Column(db.String(90), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f("Patient('{self.first_name}', '{self.last_name}', '{self.age}', "
                 "'{self.gender}','{self.latitude}','{self.longitude}', '{self.file}', '{self.date_posted}')")

# class ngo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(30),nullable=True)
#     latitude = db.Column(db.String(20), nullable=True)
#     longitude = db.Column(db.String(20), nullable=True)
#     multiple =



