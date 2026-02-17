"""
Database configuration for CET Exam App using SQLite
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# -------------------------------------------------
# SINGLE SQLAlchemy instance (VERY IMPORTANT)
# -------------------------------------------------
db = SQLAlchemy()

# -------------------------------------------------
# SQLite configuration
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "cet_exam_app.db")

# -------------------------------------------------
# Initialize DB with Flask app
# -------------------------------------------------
def init_db(app):
    print("Initializing database...")

    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind Flask app to SQLAlchemy
    db.init_app(app)

    # IMPORTANT: all DB work inside app context
    with app.app_context():

        # Import models ONLY after init_app
        import models.sql_models  # noqa: F401

        # Create tables
        db.create_all()

        # Seed default data (safe)
        from models.sql_models import SubjectCategoryModel, SubjectCategory

        for cat in SubjectCategory:
            exists = SubjectCategoryModel.query.filter_by(
                name=cat.value
            ).first()
            if not exists:
                db.session.add(
                    SubjectCategoryModel(name=cat.value)
                )

        db.session.commit()

    print("Database initialized successfully.")

# -------------------------------------------------
# Database URI
# -------------------------------------------------
def get_database_uri():
    return f"sqlite:///{SQLITE_DB_PATH}"

# -------------------------------------------------
# Engine (for background / scripts)
# -------------------------------------------------
def get_engine():
    return create_engine(
        get_database_uri(),
        connect_args={"check_same_thread": False}
    )

# -------------------------------------------------
# Scoped session (optional use)
# -------------------------------------------------
def get_db_session():
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
