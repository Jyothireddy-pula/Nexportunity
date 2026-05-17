from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def register_extensions(app):
    db.init_app(app)
