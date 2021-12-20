from operator import truediv
from qbay import app
from datetime import date
from flask_sqlalchemy import SQLAlchemy
import re


'''
This file defines data models and related business logics
'''


db = SQLAlchemy(app)

"""
User will store personal information that is used on the qbay market
"""


class User(db.Model):
    username = db.Column(
        db.String(80), nullable=False)
    email = db.Column(
        db.String(120), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    shipping_address = db.Column(db.String(120), nullable=True)
    postal_code = db.Column(db.String(120), nullable=True)
    balance = db.Column(db.Float, unique=False, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Product(db.Model):
    # The id of the product. Used to identify the product in other entities.
    id = db.Column(db.Integer, primary_key=True)
    # The price of the product. The value must be an integer.
    price = db.Column(db.Integer)
    # The title of the product.
    title = db.Column(db.String(80), unique=True, nullable=False)
    # The description of the product.
    description = db.Column(db.String(2000), unique=False, nullable=True)
    # The last modified date of the product.
    last_modified_date = db.Column(db.String(10), unique=False, nullable=False)
    # The owner's email
    owner_email = db.Column(db.String(1000), unique=False, nullable=False)


"""
Lays out the attributes for reviews that verified users can place on products
with a comment and a rating that can be liked or disliked
"""


class Review(db.Model):
    # The primary key id for each review on any product
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(120), unique=False, nullable=False)
    # Integer rating from 1 to 5 stars that the user can rate
    score = db.Column(db.Integer, unique=False, nullable=False)
    # String to contain the user's comment
    review = db.Column(db.String(300), unique=False, nullable=False)


"""
Data base table storing each succesful transaction that takes place on Qbay
"""


class Transaction(db.Model):
    # The id of the product. Used to identify the product in other entities.
    id = db.Column(db.Integer, primary_key=True)
    # The price of the product. The value must be an integer.
    price = db.Column(db.Integer)
    # The title of the product.
    title = db.Column(db.String(80), nullable=False)
    # The description of the product.
    description = db.Column(db.String(2000), unique=False, nullable=True)
    # The last modified date of the product.
    last_modified_date = db.Column(db.String(10), unique=False, nullable=False)
    # The owner's email
    owner_email = db.Column(db.String(1000), unique=False, nullable=False)


# create all tables
db.create_all()


# Model for placing an order


def place_order(email, title):
    user = User.query.filter_by(email=email).one_or_none()
    product = Product.query.filter_by(title=title).one_or_none()
    print(product.title)
    
    if product is None or user is None:
        return False
            
    # Price cannot be greater than user's balance
    if(product.price > user.balance):
        return False
    # User cannot buy from themselves
    elif(product.owner_email == user.email):
        return False
    else:
        # If successful, subtract product price from user balance
        user.balance = user.balance - product.price
        # Creates transaction item in database
        new_transaction = Transaction(price=product.price, title=product.title,
                                      last_modified_date=(product.
                                                          last_modified_date),
                                      description=product.description,
                                      owner_email=user.email) 
        db.session.delete(product)
        db.session.add(new_transaction)
        db.session.commit()
        return True


def get_transaction(email):
    # Gets all the transactions of a user
    transaction = Transaction.query.filter_by(owner_email=email).all()
    return transaction


def get_products(email):
    product_list = Product.query.filter_by(owner_email=email).all()
    return product_list


def get_listings(email):
    product_list = Product.query.filter(Product.owner_email != email).all()
    return product_list


def update_product(new_price, new_title, 
                   new_description, title):
    # Checks if product exists and creates a list of exisiting products
    product_list = Product.query.filter_by(title=title).all()
    if len(product_list) < 1:
        return False

    # Updates every existing product object to new inputed values
    for existed_product in product_list:
        # Checks if characters in the title are alphanumerical
        for character in new_title:
            if new_title.index(character) == 0:
                if character == " ":
                    return False
            if new_title.index(character) == len(new_title) - 1:
                if character == " ":
                    return False
            ascii_value = ord(character)
            if ((ascii_value >= 33 and ascii_value <= 47) or
               (ascii_value >= 58 and ascii_value <= 64) or
               (ascii_value >= 123 and ascii_value <= 126)):
                return False
        # Checks if title is long enough
        if len(new_title) > 80:
            return False
        existed_product.title = new_title

        # Checks if description is within range
        if (len(new_description) < 20 or len(new_description) > 2000 or
           len(new_description) <= len(title)):
            return False
        existed_product.description = new_description

        # Checks if the new price is greater than the old price
        if(existed_product.price > new_price):
            return False
        # Checks if price is within range
        if new_price < 10 or new_price > 10000:
            return False
        existed_product.price = new_price
        
        # Gets the current last modified date
        last_date = existed_product.last_modified_date

        # Sets the last modified date to current date
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        existed_product.last_modified_date = current_date[6:10] + \
            "-" + current_date[3:5] + "-" + current_date[0:3]

        db.session.add(existed_product)
        db.session.commit()
    return True


def create_product(price, title, description, last_modified_date, owner_email):

    # Checks if characters in the title are alphanumerical
    for character in title:
        if title.index(character) == 0:
            if character == " ":
                return False
        if title.index(character) == len(title) - 1:
            if character == " ":
                return False
        ascii_value = ord(character)
        if ((ascii_value >= 33 and ascii_value <= 47) or
           (ascii_value >= 58 and ascii_value <= 64) or
           (ascii_value >= 123 and ascii_value <= 126)):
            return False

    # Checks if title is long enough
    if len(title) > 80:
        return False

    # Checks if description is within range
    if (len(description) < 20 or len(description) > 2000 or
       len(description) <= len(title)):
        return False

    # Checks if price is within range
    if price < 10 or price > 10000:
        return False

    # Checks if year is within range
    if last_modified_date[4] != "-" or last_modified_date[7] != "-":
        return False
    last_modified_year = int(last_modified_date[0:4])
    if last_modified_year < 2021 or last_modified_year > 2025:
        return False
    last_modified_month = int(last_modified_date[5:7])
    if last_modified_month < 1 or last_modified_month > 12:
        return False
    last_modified_day = int(last_modified_date[8:10])
    if last_modified_day < 1 or last_modified_day > 31:
        return False

    # Year range check but if year is 2021
    if last_modified_year == 2021:
        if last_modified_month == 1:
            if last_modified_day < 2:
                return False

    # Year range check but if year is 2025
    if last_modified_year == 2025:
        if last_modified_month > 1:
            return False
        else:
            if last_modified_day >= 2:
                return False

    # Check if owner email is empty
    if owner_email is None:
        return False

    # Check if owner email already exists
    existed_emails = User.query.filter_by(email=owner_email).all()
    if len(existed_emails) < 1:
        return False

    # Check if product already exists
    existed_titles = Product.query.filter_by(title=title).all()
    if len(existed_titles) >= 1:
        return False

    # Creates the product and adds it into the database
    new_product = Product(price=price, title=title, description=description,
                          last_modified_date=last_modified_date,
                          owner_email=owner_email)
    db.session.add(new_product)
    db.session.commit()

    return True


def register(name, email, password):
    '''
    Register a new user
      Parameters:
        name (string):     user name
        email (string):    user email
        password (string): user password
      Returns:
        True if registration succeeded otherwise False
    '''

    # check if the email has been used:
    existed = User.query.filter_by(email=email).all()
    if len(existed) > 0:
        return False

    # check if email or password are empty
    if (len(email.strip()) == 0 or len(password.strip()) == 0):
        return False

    # check if username is not between 2 and 20 characters or is empty
    if len(name.strip()) < 2 or len(name.strip()) > 20:
        return False

    # check if username contains space at begining or end
    if (name[0] == ' ' or name[-1] == ' '):
        return False

    # check if username contains only alphanumeric characters
    if (name.replace(' ', '').isalnum() is False):
        return False

    if '@' not in email:
        return False

    email_parts = email.split('@')
    local = email_parts[0]
    domain = email_parts[1]

    # Checks there are no double quotes before running dot-string validation
    # regex
    if local.find('\"') == -1:

        # This regex checks 5 criteria: the expression is between 1-64
        # characters, does not start or end with a dot '.', there are no
        # consecutive dots and the name is made of alphanumeric and specific
        # special/printable characters
        validate_local = re.compile(
            r"^(?=.{1,64}$)(?![.])(?!.*[.]$)(?!.*?[.]{2})"
            r"[\w!#$%&*+-/=?^`{|}~]+$")

        # If local is not a perfect match against validate_local, it is an
        # invalid name
        if re.fullmatch(validate_local, local) is None:
            return False

    # Checks local name against quoted-string regex if the first and last
    # characters are double quotes. The regex checks the quoted string is
    # between 1-62 characters because an empty string is not valid and the
    # first and last characters are double quotes ' " '
    elif local.find('\"') == 0 and local.find('\"', 1) == len(local) - 1:

        # This regex checks the quoted string is made of alphanumeric
        # characters, most printable characters and special characters.
        # There is no limitation on repetition
        validate_local = re.compile(r"^(?=.{1,62}$)"
                                    r"[\w\s!#$%&*+-/=?^\"`{|}~(),:;<>@[\]]+$"
                                    )

        # If local is not a perfect match against validate_local, it is an
        # invalid name
        if re.fullmatch(validate_local, local[1:-1]) is None:
            return False

    else:

        # Informs user that local names cannot contain both quoted and
        # unquoted text
        print('''An email local name is either a Dot-string or a
        Quoted-string; it cannot be a combination.''')
        return False

    # If domain starts with '[' and ends with ']' it gets checked against
    # IPv4 and IPv6 domain rules. Dual addresses fail check.
    if domain.find('[') == 0 and domain.find(']', -1) == len(domain) - 1:

        # Validates normal IPv4 and IPv6 addresses
        validate_domain = re.compile("(?=.{1,39}$)(((25[0-5]|2[0-4][0-9]|[01]?"
                                     "[0-9][0-9]?)[.]){3}(25[0-5]|2[0-4][0-9]|"
                                     "[01]?[0-9][0-9]?))"

                                     # If the string doesn't match against IPv4
                                     # rules, check against IPv6 rules
                                     "|"

                                     # Validates normal IPv6 addresses
                                     "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]"
                                     "{1,4}|"
                                     "([0-9a-fA-F]{1,4}:){1,7}:|"
                                     "([0-9a-fA-F]{1,4}:){1,6}:"
                                     "[0-9a-fA-F]{1,4}|"
                                     "([0-9a-fA-F]{1,4}:){1,5}"
                                     "(:[0-9a-fA-F]{1,4}){1,2}|"
                                     "([0-9a-fA-F]{1,4}:){1,4}"
                                     "(:[0-9a-fA-F]{1,4}){1,3}|"
                                     "([0-9a-fA-F]{1,4}:){1,3}"
                                     "(:[0-9a-fA-F]{1,4}){1,4}|"
                                     "([0-9a-fA-F]{1,4}:){1,2}"
                                     "(:[0-9a-fA-F]{1,4}){1,5}|"
                                     "[0-9a-fA-F]{1,4}:"
                                     "((:[0-9a-fA-F]{1,4}){1,6})|"
                                     ":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
                                     "fe80:(:[0-9a-fA-F]{0,4}){0,4}%"
                                     "[0-9a-zA-Z]{1,}|"
                                     "::(ffff(:0{1,4}){0,1}:){0,1}"
                                     "((25[0-5]|(2[0-4]|1{0,1}[0-9])"
                                     "{0,1}[0-9])[.]{3,3}"
                                     "(25[0-5]|(2[0-4]|1{0,1}[0-9])"
                                     "{0,1}[0-9])|"
                                     "([0-9a-fA-F]{1,4}:){1,4}:"
                                     "((25[0-5]|(2[0-4]|1{0,1}[0-9])"
                                     "{0,1}[0-9])[.]){3,3}"
                                     "(25[0-5]|(2[0-4]|1{0,1}[0-9])"
                                     "{0,1}[0-9])))")

        # If domain is not a perfect match against validate_domain, it is an
        # invalid address
        if re.fullmatch(validate_domain, domain[1:-1]) is None:
            return False

    # Checks the domain against LDH domain rules
    else:
        validate_domain = re.compile(
            # Checks the domain for five criteria: it is between 1 and 63
            # characters long, it does not start or end with a hyphen '-',
            # there is one dot '.', and every other character is
            # a-z, A-Z, 0-9, -, or . for subdomains
            r"^(?=.{1,63}$)(?![-])(?!.*[-])[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

        # If domain is not a perfect match against validate_domain, it is an
        # invalid address
        if re.fullmatch(validate_domain, domain) is None:
            return False

    # check if password is at least 6 characters long
    if len(password) < 6:
        return False

    # counting upercase, lowercase, and special characters in supplied password
    uppercase_count = 0
    lowercase_count = 0
    special_count = 0
    for char in password:
        ascii_value = ord(char)
        if (ascii_value >= 65) and (ascii_value <= 90):  # char is uppercase
            uppercase_count += 1
        elif (ascii_value >= 97) and (ascii_value <= 122):  # char is lowercase
            lowercase_count += 1
        # char is special character except space char
        elif ((ascii_value >= 33 and ascii_value <= 47) or
              (ascii_value >= 58 and ascii_value <= 64) or
              (ascii_value >= 123 and ascii_value <= 126)):
            special_count += 1
        else:
            continue

    # check if password has at least one upercase, lowercase, and
    # special characters in supplied password
    if (uppercase_count == 0 or lowercase_count == 0 or
       special_count == 0):
        return False

    # creates a new user
    user = User(username=name, email=email, password=password,
                shipping_address=None, postal_code=None, balance=100)
    # add it to the current database session
    db.session.add(user)
    # actually save the user object
    db.session.commit()

    return True


def login(email, password):
    '''
    Check login information
      Parameters:
        email (string):    user email
        password (string): user password
      Returns:
        The user object if login succeeded otherwise None
    '''

    # check if email or password are empty
    if len(email.strip()) == 0 or len(password.strip()) == 0:
        return None

    # check if password is at least 6 characters long
    if len(password) < 6:
        return None

    # counting upercase, lowercase, and special characters in supplied password
    uppercase_count = 0
    lowercase_count = 0
    special_count = 0
    for char in password:
        ascii_value = ord(char)
        if (ascii_value >= 65) and (ascii_value <= 90):  # char is uppercase
            uppercase_count += 1
        elif (ascii_value >= 97) and (ascii_value <= 122):  # char is lowercase
            lowercase_count += 1
        # char is special character except space char
        elif ((ascii_value >= 33 and ascii_value <= 47) or
              (ascii_value >= 58 and ascii_value <= 64) or
              (ascii_value >= 123 and ascii_value <= 126)):
            special_count += 1
        else:
            continue

    # check if password has at least one upercase, lowercase, and
    # special characters in supplied password
    if (uppercase_count == 0 or lowercase_count == 0 or
       special_count == 0):
        return None

    # Finds and returns user in database
    valids = User.query.filter_by(email=email, password=password).all()
    if len(valids) != 1:
        return None
    print(valids[0])
    return valids[0]


def update_user(find_email, new_name=None,
                new_shipping_address=None, new_postal_code=None):
    '''
    updates a existing user
      Parameters:
        find_email (string):    user email
        new_name (string):    modified username
        new_shipping_address (string): modified shipping address
        new_postal_code (string): modified postal code
      Returns:
        True if updating user info succeeded otherwise False
    '''

    modify_user_list = User.query.filter_by(email=find_email).all()
    modify_user = modify_user_list[0]

    # Updating Username
    if (new_name is not None):
        # check if username is not between 2 and 20 characters or is empty
        if (len(new_name.strip()) < 2 or len(new_name.strip()) > 20):
            return False
        # check if username contains space at begining or end
        elif (new_name[0] == ' ' or new_name[-1] == ' '):
            return False
        # check if username contains only alphanumeric characters
        elif (new_name.replace(' ', '').isalnum() is False):
            return False
        else:
            modify_user.username = new_name

    # Updating Shipping address
    if (new_shipping_address is not None):
        # check if new shipping address is non-empty
        if (len(new_shipping_address.strip()) == 0):
            return False
        # check if new shipping address contains only alphanumeric characters
        elif (new_shipping_address.replace(" ", "").isalnum() is False):
            return False
        else:
            modify_user.shipping_address = new_shipping_address

    # Updating Postal Code
    if (new_postal_code is not None):

        # Validate_postal checks a string follows the format
        # x0x 0x0 where x is one of A,B,C,E,G,H,J,K,L,M,N,P,R,S,T,V,X,Y
        # and 0 is any digit from 0-9
        validate_postal = re.compile(r"[ABCEGHJKLMNPRSTVXY]\d"
                                     r"[ABCEGHJKLMNPRSTVXY][\s]?\d"
                                     r"[ABCEGHJKLMNPRSTVXY]\d")

        # If new_postal_code is not a perfect match against
        # validate_postal, it is not a valid Canadian postal code
        if re.fullmatch(validate_postal, new_postal_code) is None:
            return False

        modify_user.postal_code = new_postal_code

    db.session.add(modify_user)
    db.session.commit()
    return True
