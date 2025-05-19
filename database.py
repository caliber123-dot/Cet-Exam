"""
Database configuration for CET Exam App with PostgreSQL
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    print('Initialize database with app context')
    """Initialize database with app context"""
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()

def get_database_uri():
    """Get database URI from environment variables or use default"""
    db_user = os.getenv('DB_USERNAME', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'password')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'cet_exam_app')
    # print(db_password)
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def get_engine():
    """Get SQLAlchemy engine for direct connection if needed"""
    return create_engine(get_database_uri())

def get_db_session():
    """Get a scoped database session for operations outside request context"""
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
