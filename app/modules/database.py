from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql import func
from datetime import datetime
import string,random
import logging
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()


AUTHORIZATION_VALID_TIME = 10 # days
VALIDATION_TOKEN_LIFE = 3 # days
PASSWORD_RESET_TOKEN_LIFE = 2 # days

class BaseMixin(object):
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(BaseMixin,Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False,unique=True)
    first_name = Column(String,nullable=True,default=None)
    last_name = Column(String,nullable=True,default=None)
    created = Column(DateTime(timezone=True),nullable=False, default=func.now())
    last_seen = Column(DateTime(timezone=True),default=func.now())
    password = Column(String,nullable=False)
    password_created = Column(DateTime(timezone=True),nullable=False,default=func.now())
    email_validated = Column(Boolean,nullable=False,default=False)
    email_validation_token = Column(String,nullable=True,default=None)
    email_validation_token_created = Column(DateTime(timezone=True),nullable=True, default=None)
    authorized = Column(Boolean,nullable=False,default=False)
    authorized_time = Column(DateTime(timezone=True),nullable=False, default=func.now())
    type = Column(Integer,nullable=False,default=0)
    token = Column(String,nullable=True,default=None)
    password_reset_token = Column(String,nullable=True,default=None)
    password_reset_token_created = Column(DateTime(timezone=True),nullable=True, default=None)

    @staticmethod
    def retrieve_clean_obj_data(obj,include_token = False,public=False):
        obj = obj.as_dict()
        if include_token:
            return {
                "id": obj['id'],
                "email": obj['email'],
                "token": obj['token'],
                "first_name": obj['first_name'],
                "last_name": obj['last_name'],
                "type": obj['type']
            }
        elif public:
            return {
                "id": obj['id'],
                "first_name": obj['first_name'],
                "last_name": obj['last_name'][:1]
            }
        else:
            return {
                "id": obj['id'],
                "email": obj['email'],
                "first_name": obj['first_name'],
                "last_name": obj['last_name'],
                "type": obj['type']
            }


    @staticmethod
    def login_user(email_or_username,password):
        db = next(get_db())
        user = False
        user = db.query(User).filter_by(email=email_or_username).first()
        if not user:
            db.close()
            return False, "User not found."

        if user.password != password:
            db.close()
            return False, "Invalid password."

        if user.email_validated == False:
            db.close()
            return False, "You must first verify your email."
        
        user.last_seen = datetime.now()
        db.commit()
        user_as_dict = user.as_dict()
        db.close()
        return True, user_as_dict

    @staticmethod
    def user_types():
        return {
            0:"User",
            1:"Agent",
            99:"Admin"
        }

    @staticmethod
    def is_authorized(id):
        db = next(get_db())
        user = db.query(User).get(id)
        db.close()
        return user.authorized and (datetime.today()-user.authorized_time).total_seconds()/60/60/24 < AUTHORIZATION_VALID_TIME

    @classmethod
    def authorize(id):
        db = next(get_db())
        user = db.query(User).get(id)
        user.authorized=True
        user.authorized_time = datetime.now()
        db.commit()
        db.close()
        return True

    @staticmethod
    def validate_email(id,validation_token):
        db = next(get_db())
        user = db.query(User).get(id)
        print(user.email_validation_token_created)
        print(datetime.now())
        if user.email_validation_token == validation_token and (datetime.now() - user.email_validation_token_created).total_seconds()/60/60/24 < VALIDATION_TOKEN_LIFE:
            user.email_validated = True
            user.email_validation_token = None
            db.commit()
            db.close()
            return True, "", -1
        elif user.email_validation_token != validation_token:
            db.close()
            return False, "Email validation token is not correct.", 1
        else:
            # time expired
            db.close()
            return False, "Email validation token expired. Please request another.", 2

    @staticmethod
    def generate_password_reset_token(id):
        db = next(get_db())
        user = db.query(User).get(id)
        size = 25
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k = size))
        user.password_reset_token = token
        user.password_reset_token_created = datetime.now()
        db.commit()
        db.close()
        return token

    @staticmethod
    def update_user_password(id,password,password_reset_token=False):
        db = next(get_db())
        user = db.query(User).get(id)
        if password_reset_token:
            if not user.password_reset_token:
                return False,"There isn't a password reset request for this user."
            if (datetime.now().astimezone() - user.password_reset_token_created).total_seconds()/60/60/24 > PASSWORD_RESET_TOKEN_LIFE:
                return False, "Your password reset token has expired."
            if user.password_reset_token != password_reset_token:
                return False, "Reset token invalid."
        success, msg = User.validate_password_field(password)
        if not success:
            db.close()
            return success, msg
        user.password=password
        user.password_created = datetime.now()
        user.password_reset_token = None
        user.password_reset_token_created = None
        db.commit()
        db.close()
        return True, "Your password has been changed."
            
    @staticmethod
    def validate_password_field(password):
        password = str(password)
        if len(password)<8:
            return False, "Password must be at least 8 characters long"
        return True, ""

    @staticmethod
    def generate_email_validation_token(id):
        db = next(get_db())
        user = db.query(User).get(id)
        if user.email_validated:
            db.close()
            return False, "Email already validated"
        size = 25
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k = size))
        user.email_validation_token = token
        user.email_validation_token_created = datetime.now()
        db.commit()
        db.close()
        return token, ""


