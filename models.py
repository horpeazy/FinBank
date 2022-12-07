from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(200))

class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(15), nullable=False, unique=True)
    first_name = db.Column(db.String(40), nullable=False)
    middle_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40), nullable=False)
    dob = db.Column(db.DateTime)
    account_balance = db.Column(db.Integer)
    profile_image = db.Column(db.LargeBinary)
    id_image = db.Column(db.LargeBinary)
    id_number = db.Column(db.String(20))
    email_address = db.Column(db.String(80))
    phone_number = db.Column(db.String(20))
    alt_phone_number = db.Column(db.String(20))
    home_address = db.Column(db.String(200))
    alt_home_address = db.Column(db.String(200))
    city = db.Column(db.String(40))
    state = db.Column(db.String(40))
    country = db.Column(db.String(40))
    zip_code = db.Column(db.String(20))
    transaction_pin = db.Column(db.Integer, nullable=False)

    # foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_name = db.Column(db.String(80))
    receiver_name = db.Column(db.String(80))
    narration = db.Column(db.String(200))
    amount = db.Column(db.Integer, nullable=False)
    fee = db.Column(db.Integer, nullable=False)
    transaction_time = db.Column(db.DateTime)
    status = db.Column(db.Boolean)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    members = db.Column(db.PickleType, nullable=False)

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000), nullable=False)
    sender_name = db.Column(db.String(80), nullable=False)
    receiver_name= db.Column(db.String(80), nullable=False)
    room_name = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "text": self.text,
            "sender_name": self.sender_name,
            "receiver_name": self.receiver_name,
            "room_name": self.room_name,
            "timestamp": self.timestamp.strftime("%d %b, %H:%M")
        }
