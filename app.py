from datetime import datetime
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Account, Transaction
from forms import LoginForm, RegisterForm, AccountForm
from flask_mail import Mail, Message
from utils import generate_account, generate_token

# initialize flask app
app = Flask(__name__)
mail = Mail(app) # instantiate the mail class
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:afisuru123@localhost:5432/testfinbank'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'iyamuhope.nosa647@gmail.com'
app.config['MAIL_PASSWORD'] = "vvuhkoulfdwhqyvu"
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

def send_token(recipient, token):
    try:
        msg = Message(
                        'OTP Verification Code',
                        sender =('FinBank', 'iyamuhope.nosa647@gmail.com'),
                        recipients = [recipient],

                    )
        msg.body = "Please use the following OTP code {} to complete your transaction.".format(token)
        result = mail.send(msg)
        print(result)
    except:
        raise Exception

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d,"
  elif format == 'medium':
      format="dd MMM 'at' H:mm"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


@app.route('/register', methods=['GET', 'POST'])
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
    user_id = current_user.ged_id()
    account = Account.query.filter_by(user_id=user_id).first()
    transactions = Transaction.query.filter_by(sender_id=user_id).first()
    data = {
        "title": "Personal Information",
        "account": account
    }
    return render_template("profile.html", data=data)

@app.route("/card")
def card():
    return render_template("card.html", data={"title": "Cards"})

@app.route("/accounts")
def accounts():
    return render_template("all-accounts.html", data={"title": "Accounts"})

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
                new_account.account_balance = 0
                new_account.transaction_pin = 1234
                hashed_password = bcrypt.\
                                generate_password_hash("newuserpass123").\
                                decode("utf-8")
                username = form.first_name.data.lower() + form.last_name.data.lower() + "123"
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.flush()
                new_user = User.query.filter_by(username=username).first()
                new_account.user_id = new_user.id
                db.session.add(new_account)
                db.session.commit()
                return render_template("account-success.html", data={"title": "Application Sent"})
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    return render_template("create-account.html", data=data)

@app.route("/loans")
@login_required
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

@app.route("/dashboard")
@login_required
def account():
    user_id = current_user.get_id()
    print(user_id)
    account = Account.query.filter_by(user_id=user_id).first()
    transactions = Transaction.query.filter(or_(Transaction.sender_id==user_id, Transaction.receiver_id==user_id)).\
        join(Account, Transaction.receiver_id == Account.id).all()
    data = {
        "title": "Dashboard",
        "account": account,
        "transactions": transactions,
        "user_id": int(user_id)
    }
    return render_template("dashboard.html", data=data)

@app.route("/transactions")
@login_required
def transactions():
    user_id = current_user.get_id()
    print(user_id)
    account = Account.query.filter_by(user_id=user_id).first()
    transactions = Transaction.query.filter(or_(Transaction.sender_id==user_id, Transaction.receiver_id==user_id)).\
        join(Account, Transaction.receiver_id == Account.id).all()
    data = {
        "title": "Trasaction History",
        "account": account,
        "transactions": transactions,
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
            fee = amount * 0.005
            if amount >= (account.account_balance - fee):
                flash("Insufficient Funds")
                return render_template("send-money.html", data=data)      
            token = generate_token()
            send_token(account.email_address, token)
            session["token"] = token
            session["sender_id"] = account.id
            session["receiver_id"] = dest_acc.id
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
            receiver_account = Account.query.filter_by(id=receiver_id).first()
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
            return redirect(url_for("send_money"))

    return redirect(url_for("send_money"))

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html", data={"title": "Forgot Password"})

@app.route("/change-password")
def change_password():
    return render_template("change-password.html", data={"title": "Change Password"})

@app.route("/link-sent")
def link_sent():
    return render_template("link-sent.html", data={"title": "Link Sent"})


# TODO

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
    
    

if __name__ == "__main__":
    app.run(debug=True)
