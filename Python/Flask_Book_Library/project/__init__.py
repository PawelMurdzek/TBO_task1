import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from markupsafe import escape

# Database Setup
app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecret' # To allow us to use forms
app.config["TEMPLATES_AUTO_RELOAD"] = True

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)


# Content Security Policy header
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = (
        "font-src 'self' https://stackpath.bootstrapcdn.com https://use.fontawesome.com data:; "
        "img-src 'self' data:;"
    )
    return response


# Register Blueprints
from project.core.views import core
from project.books.views import books
from project.customers.views import customers
from project.loans.views import loans

app.register_blueprint(core)
app.register_blueprint(books)
app.register_blueprint(customers)
app.register_blueprint(loans)