import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_ckeditor import CKEditor

app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    ckeditor = CKEditor(app)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

# Import all the controllers so they are loaded
from application.controllers import *

if __name__ == '__main__':
  # Run the Flask app
  # db.create_all()
  app.run(host='0.0.0.0',port=8080)