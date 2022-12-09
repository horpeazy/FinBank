from datetime import datetime
import os
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, url_for, redirect, flash, session, abort
import logging
from logging import Formatter, FileHandler
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS
from sqlalchemy import or_
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from models import Room, db, User, Account, Transaction, Messages
from forms import LoginForm, RegisterForm, AccountForm
from flask_mail import Mail, Message
from utils import generate_account, generate_token
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_handlers=True) #, ping_timeout=5, ping_interval=5)
mail = Mail(app)                # instantiate the mail class
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER']= os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
bcrypt = Bcrypt(app)
db.init_app(app)


with app.app_context():
    db.create_all()
Migrate(app, db)

# login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def send_message(recipient, message):
    try:
        print("Start")
        msg = Message(
                        'OTP Verification Code',
                        sender =('FinBank', 'iyamuhope.nosa647@gmail.com'),
                        recipients = [recipient],
                    )
        print("continue")
        msg.body = message
        result = mail.send(msg)
    except:
        print(sys.exc_info())
        raise Exception



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'small':
      format="HH:mm"
  elif format == 'medium':
      format="dd MMM 'at' HH:mm"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    data = {
        "form": form,
        "title": "Login"
    }
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    return render_template('login.html', data=data)
            else:
                return render_template('login.html', data=data)
        else:
            return render_template('login.html', data=data)
    return render_template('login.html', data=data)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    data = {
        "form": form,
        "title": "Register"
    }
    if request.method == "POST":
        try:
            if form.validate_on_submit():
                hashed_password = bcrypt.\
                                generate_password_hash(form.password.data).\
                                decode("utf-8")
                new_user = User(username=form.username.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        except Exception:
            print(sys.exc_info())
            flash("Error occurred during registeration")
    return render_template('register.html', data=data)

@app.route("/admin/users")
@login_required
def all_users():
    if current_user.username != "admin":
        abort(404)
    users = User.query.all()
    data = {
        "title": "Users",
        "users": users
    }
    return render_template("users.html", data=data)

@app.route('/images/<int:id>/logo')
def image_url(id):
    image = Account.query.get_or_404(id)
    return app.response_class(image.profile_image, mimetype='application/octet-stream')

@app.route("/")
def home():
    print(current_user.get_id())
    return render_template("home.html", data={"title": "Home"})

@app.route("/profile")
@login_required
def profile():
    user_id = current_user.get_id()
    account = Account.query.filter_by(user_id=user_id).first()
    transactions = Transaction.query.filter_by(sender_id=user_id).first()
    data = {
        "title": "Personal Information",
        "account": account
    }
    return render_template("profile.html", data=data)

@app.route("/create-account", methods=['GET', 'POST'])
def create_account():
    form = AccountForm()
    data = {
        "title": "Create Account",
        "form": form
    }
    if request.method == "POST":
        try:
            if form.validate_on_submit():
                new_account = Account()
                form.populate_obj(new_account)
                new_account.account_number = generate_account()
                if request.form.get("first_name") == "admin":
                    new_account.account_balance = 100000000
                else:
                    new_account.account_balance = 0
                new_account.transaction_pin = 1234
                hashed_password = bcrypt.\
                                generate_password_hash("newuserpass123").\
                                decode("utf-8")
                if request.form.get("first_name") == "admin":
                    username = "admin"
                else:
                    username = form.first_name.data.lower() + form.last_name.data.lower()
                full_name = request.form.get("last_name") + " " + request.form.get("first_name")
                new_user = User(username=username, password=hashed_password, full_name=full_name)
                db.session.add(new_user)
                db.session.flush()
                new_user = User.query.filter_by(username=username).first()
                new_account.user_id = new_user.id
                new_room = Room(room_name=username, members=["admin", username])
                db.session.add_all([new_account, new_room])
                db.session.commit()
                return render_template("account-success.html", data={"title": "Application Sent"})
            else:
                flash("Invalid form")
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    return render_template("create-account.html", data=data)

@app.route("/admin/user/edit/<int:user_id>", methods=["POST", "GET"])
@login_required
def edit_user(user_id):
    if current_user.username != "admin":
        return render_template("404.html", data={'title': "404"})
    account = Account.query.filter_by(user_id=user_id).first()
    if not account:
        flash("Accout doesn't exist")
        return redirect(url_for("all_users"))
    if request.method == "POST":
        try:
            form = AccountForm(request.form, obj=account)
            if form.validate_on_submit():
                form.populate_obj(account)
                db.session.commit()
                return redirect(url_for("all_users"))
        except:
            print(sys.exc_info())
            db.session.rollback()
            flash("An error occured")
            return redirect(url_for("all_users"))
    form = AccountForm(obj=account)
    data = {
        "title": "Edit Account",
        "form": form
    }
    return render_template("edit-account.html", data=data)

@app.route("/admin/load-account", methods=["POST", "GET"])
@login_required
def load_account():
    if current_user.username != "admin":
        return render_template("404.html", data={'title': "404"})
    if request.method == "POST":
        try:
            amount = int(request.form.get("amount"))
            account = Account.query.filter_by(first_name="admin").first()
            account.account_balance = account.account_balance + amount
            db.session.add(account)
            db.session.commit()
            return redirect(url_for("account"))
        except:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)
    return render_template("load-account.html", data={"title": "Load Account"})

@app.route("/dashboard")
@login_required
def account():
    user_id = current_user.get_id()
    account = Account.query.filter_by(user_id=user_id).first()
    transactions = Transaction.query.filter(or_(Transaction.sender_id==user_id, Transaction.receiver_id==user_id)).all()
    data = {
        "title": "Dashboard",
        "account": account,
        "transactions": transactions[::-1],
        "user_id": int(user_id)
    }
    return render_template("dashboard.html", data=data)

@app.route("/transactions")
@login_required
def transactions():
    user_id = current_user.get_id()
    print(user_id)
    account = Account.query.filter_by(user_id=user_id).first()
    transactions = Transaction.query.filter(or_(Transaction.sender_id==user_id, Transaction.receiver_id==user_id)).all()
    data = {
        "title": "Trasaction History",
        "account": account,
        "transactions": transactions[::-1],
        "user_id": int(user_id)
    }
    return render_template("transactions.html", data=data)

@app.route("/send-money", methods={"POST", "GET"})
@login_required
def send_money():
    user_id = current_user.get_id()
    account = Account.query.filter_by(user_id=user_id).first()
    data = {
        "title": "Transfer Money",
        "account": account
    }
    if request.method == "POST":
        try:
            dest_acc_number = request.form.get("dest_acc_number")
            amount = int(request.form.get("amount"))
            narration = request.form.get("narration")
            pin = int(request.form.get("pin"))
            dest_acc = Account.query.filter_by(account_number=dest_acc_number).first()
            if not dest_acc:
                flash("Sorry, account doesn't exist")
                return redirect(url_for("send_money"))
            user_pin = account.transaction_pin
            if pin != user_pin:
                flash("Incorrect pin")
                return render_template("send-money.html", data=data)
            fee = amount * 0.01
            if amount >= (account.account_balance - fee):
                flash("Insufficient Funds")
                return render_template("send-money.html", data=data)      
            token = generate_token()
            message = "Please use the following OTP code {} to complete your transaction.".format(token)
            send_message(account.email_address, message)
            session["token"] = token
            session["sender_id"] = account.user_id
            session["receiver_id"] = dest_acc.user_id
            session["sender_name"] = account.first_name + " " + account.last_name
            session["receiver_name"] = dest_acc.first_name + " "  + dest_acc.last_name
            session["narration"] = narration
            session["amount"] = amount
            session["fee"] = fee
            data = {
                "title": "Confirm Transaction",
                "source_account": account.account_number,
                "bank_name": "FinBank",
                "dest_account": dest_acc_number,
                "dest_name": dest_acc.first_name + " "  + dest_acc.last_name,
                "narration": narration,
                "amount": amount,
                "fee": fee,
                "total": amount + fee
            }
            return render_template("send-money-confirm.html", data=data)
        except Exception:
            flash("Error while processiog transaction")
            print(sys.exc_info())
            
    return render_template("send-money.html", data=data)

@app.route("/send-money-confirm", methods=["POST", "GET"])
@login_required
def send_money_confirm():
    user_id = current_user.get_id()
    account = Account.query.filter_by(user_id=user_id).first()
    data = {
        "title": "Transfer Money",
        "account": account
    }
    if request.method == "POST":
        try:
            token = session["token"]
            sender_id = session["sender_id"]
            receiver_id = session["receiver_id"]
            narration = session["narration"]
            amount = int(session["amount"])
            fee = int(session["fee"])
            sender_name = session["sender_name"]
            receiver_name = session["receiver_name"]
            sender_token = int(request.form.get("token"))
            receiver_account = Account.query.filter_by(user_id=receiver_id).first()
            if token != sender_token:
                flash("Inavlid OTP code")
                data = {
                    "title": "Transfer Money",
                    "account": account
                }
                return redirect(url_for("send_money"))
            account.account_balance = account.account_balance - (amount + fee)
            receiver_account.account_balance = receiver_account.account_balance + amount
            transaction = Transaction(
                sender_id=sender_id,
                receiver_id=receiver_id,
                sender_name=sender_name,
                receiver_name=receiver_name,
                narration=narration,
                amount=amount,
                fee=fee,
                transaction_time=datetime.now(),
                status=True 
            )
            db.session.add_all([account, receiver_account, transaction])
            db.session.commit()
            session["token"] = None
            session["sender_id"] = None
            session["receiver_id"] = None
            session["sender_name"] = None
            session["receiver_name"] =  None
            session["narration"] = None
            session["amount"] = None
            session["fee"] = None
            data = {
                "title": "Success",
                "amount": amount,
                "receiver_name": receiver_name
            }
            return render_template("send-money-success.html", data=data)
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            return redirect(url_for("send_money"))

    return redirect(url_for("send_money"))

@app.route("/forgot-password", methods=["POST", "GET"])
def forgot_password():
    if request.method == "POST":
        try:
            account = Account.query.filter_by(email_address=request.form.get("email_address"))
            if not account:
                flash("Invalid credential")
                return render_template("forgot-password.html", data={"title": "Forgot Password"})
            user_id = account.user_id
            user = User.query.filter_by(id=user_id).first()
            newpassword = "resetpassword123"
            message = "Your new password is {}, please change this password once you login".\
                        format(newpassword)
            send_message(request.form.get("email_address"), message)
            hashed_password = bcrypt.generate_password_hash(newpassword).\
                                    decode("utf-8")
            user.password = hashed_password
            db.session.add(user)
            db.session.commit()
            return render_template("forgot-password-success.html", data={"title": "Forgot Password"})
        except:
            print(sys.sec_info())
            flash("An error occured")
            return render_template("forgot-password.html", data={"title": "Forgot Password"})
            abort(500)

    return render_template("forgot-password.html", data={"title": "Forgot Password"})

@app.route("/change-password", methods=["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        try:
            user = User.query.filter_by(id=current_user.id).first()
            if bcrypt.check_password_hash(user.password, request.form.get("old_pass")):
                if request.form.get("new_pass") == request.form.get("new_pass_confirm"):
                    if len(request.form.get("new_pass")) < 8:
                        flash("Passwords too short")
                        return render_template("change-password.html", data={"title": "Change Password"})
                    hashed_password = bcrypt.\
                                    generate_password_hash(request.form.get("new_pass")).\
                                    decode("utf-8")
                    user.password = hashed_password
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for("home"))
                else:
                    flash("New passwords do not match")
                    return render_template("change-password.html", data={"title": "Change Password"})
            else:
                flash("Old password is incorrect")
                return render_template("change-password.html", data={"title": "Change Password"})
        except:
            print(sys.exc_info())
            abort(500)
    return render_template("change-password.html", data={"title": "Change Password"})

@app.route("/change-pin", methods=["POST", "GET"])
@login_required
def change_pin():
    if request.method == "POST":
        try:
            account = Account.query.filter_by(user_id=current_user.id).first()
            if account.transaction_pin == int(request.form.get("old_pin")):
                if request.form.get("new_pin") == request.form.get("new_pin_confirm"):
                    if len(request.form.get("new_pin")) > 4:
                        flash("PIN must be 4 digits")
                        return render_template("change-pin.html", data={"title": "Change PIN"})
                    account.transaction_pin = request.form.get("new_pin")
                    db.session.add(account)
                    db.session.commit()
                    return redirect(url_for("account"))
                else:
                    flash("New pins don't match")
                    return render_template("change-pin.html", data={"title": "Change PIN"})
            else:
                flash("Old pin is incorrect")
                return render_template("change-pin.html", data={"title": "Change PIN"})
        except:
            print(sys.exc_info())
            abort(500)
    return render_template("change-pin.html", data={"title": "Change PIN"})

@app.route("/chat")
@login_required
def chat():
    room_name = request.args.get("room", "")
    try:
        room = Room.query.filter_by(room_name=room_name).first()
        if room:
            user = current_user.username
            members = room.members
            if user in members or user == "admin":
                messages = Messages.query.filter_by(room_name=room_name).all()
                members.remove(user)
                receiver = members[0]
                data = {
                    "title": "Chat",
                    "room": room,
                    "messages": messages,
                    "receiver": receiver
                }
                return render_template("chat-room.html", data=data)
            return render_template("404.html", data={"title": "404"})
        else:
            abort(500)
    except Exception:
        print(sys.exc_info())
        return render_template("404.html", data={"title": "404"})

@app.route("/withdraw", methods=["POST", "GET"])
@login_required
def payment():
    user_id = current_user.get_id()
    account = Account.query.filter_by(user_id=user_id).first()
    data = {
        "title": "Withdraw Money",
        "account": account
    }
    if request.method == "POST":
        return render_template("withdraw-failed.html", data=data)
    return render_template("withdraw.html", data=data)

@app.route("/link-sent")
def link_sent():
    return render_template("link-sent.html", data={"title": "Link Sent"})

@app.route("/loans")
def loans():
    return render_template("home-loan.html", data={"title": "Loans"})

@app.route("/home-loan")
def home_loans():
    return render_template("home-loan.html", data={"title": "Home loan"})

@app.route("/personal-loan")
def personal_loans():
    return render_template("personal-loan.html", data={"title": "Personal Loan"})

@app.route("/vehicle-loan")
def vehicle_loans():
    return render_template("vehicle-loan.html", data={"title": "Vehicle Loan"})

@app.route("/gold-loan")
def gold_loans():
    return render_template("gold-loan.html", data={"title": "Gold Loan"})

@app.route("/education-loan")
def education_loans():
    return render_template("education-loan.html", data={"title": "Education Loan"})

@app.route("/about")
def about():
    return render_template("about.html", data={"title": "About"})

@app.route("/contact")
def contact():
    return render_template("contact.html", data={"title": "Contact"})

@app.route("/board-of-directors")
def board_of_directors():
    return render_template("board-of-directors.html", data={"title": "Board Of Directors"})

@app.route("/faq")
def faq():
    return render_template("faq.html", data={"title": "FAQ'S"})

@app.route("/testimonials")
def testimonials():
    return render_template("testimonials.html", data={"title": "Testimonial"})

@app.route("/nri-account")
def nri():
    return render_template("nri.html", data={"title": "NRI"})

@app.route("/card")
def card():
    return render_template("card.html", data={"title": "Cards"})

@app.route("/accounts")
def accounts():
    return render_template("all-accounts.html", data={"title": "Accounts"})


@socketio.on('send_message')
def handle_send_message_event(data):
    try:
        with app.app_context():
            room = Room.query.filter_by(room_name=data["room"]).first()
            members = room.members
            sender_id = int(data["user_id"])
            sender = User.query.filter_by(id=sender_id).first()
            sender_name = sender.username
            members.remove(sender_name)
            receiver_name = members[0]
            new_message = Messages(sender_name=sender_name,
                                  receiver_name=receiver_name,
                                  text=data["message"],
                                  timestamp=datetime.now(),
                                  room_name=data["room"]
                                )
            db.session.add(new_message)
            db.session.commit()
            data["sender"] = sender_name
            data["timestamp"] = new_message.timestamp.strftime("%I:%M")
        socketio.emit('receive_message', data, room=data['room'])
    except Exception:
        print(sys.exc_info())
        db.session.rollback()


@socketio.on('join_room')
def handle_join_room_event(data):
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room']) 

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html", data={"title": "404"})

@app.errorhandler(500)
def server_error(error):
    return render_template("500.html", data={"title": "500"})  

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port: 
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
