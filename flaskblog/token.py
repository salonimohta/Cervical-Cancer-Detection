from itsdangerous import URLSafeTimedSerializer as Serializer
from flaskblog import app

def generate_confirmation_token(email):
    s = Serializer(app.config['SECRET_KEY'])
    return s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email
