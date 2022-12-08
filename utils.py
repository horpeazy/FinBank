import random


ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]

def generate_account():
    account_number = "2"
    for i in range(9):
        account_number = account_number + str(random.randint(0, 9))

    return account_number

def generate_token():
    token = ""
    for i in range(4):
        token = token + str(random.randint(0, 9))

    return int(token)

def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS