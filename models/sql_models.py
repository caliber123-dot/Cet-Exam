"""
SQLAlchemy models for the CET Exam App
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from database import db
import uuid

class SubjectCategory(str, Enum):
    """Enum for subject categories in the exam."""
    REASONING = "reasoning"
    ENGLISH = "english"
    COMPUTER_CONCEPTS = "computer_concepts"
    PYTHON = "python"

class User(db.Model):
    """User model for authentication and role management."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    uid = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='student')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    results = relationship("ExamResult", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, email, display_name, password_hash, role='student'):
        self.uid = str(uuid.uuid4())
        self.email = email
        self.display_name = display_name
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'uid': self.uid,
            'email': self.email,
            'displayName': self.display_name,
            'role': self.role,
            'createdAt': self.created_at,
            'lastLogin': self.last_login
        }

class Question(db.Model):
    """Question model for exam questions."""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty_level = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    exam_questions = relationship("ExamQuestion", back_populates="question", cascade="all, delete-orphan")
    result_answers = relationship("ResultAnswer", back_populates="question", cascade="all, delete-orphan")
    
    def __init__(self, text, category, explanation, difficulty_level=1):
        self.uuid = str(uuid.uuid4())
        self.text = text
        self.category = category if isinstance(category, str) else category.value
        self.explanation = explanation
        self.difficulty_level = difficulty_level
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert question to dictionary."""
        return {
            'id': self.uuid,
            'text': self.text,
            'category': self.category,
            'options': [option.to_dict() for option in self.options],
            'explanation': self.explanation,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Option(db.Model):
    """Option model for question options."""
    __tablename__ = 'options'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    option_id = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('question_id', 'option_id', name='uq_option_question_option_id'),
    )
    
    def __init__(self, question_id, option_id, text, is_correct=False):
        self.question_id = question_id
        self.option_id = option_id
        self.text = text
        self.is_correct = is_correct
    
    def to_dict(self):
        """Convert option to dictionary."""
        return {
            'id': self.option_id,
            'text': self.text,
            'is_correct': self.is_correct
        }

class Exam(db.Model):
    """Exam model for exam metadata."""
    __tablename__ = 'exams'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    categories = relationship("ExamCategory", back_populates="exam", cascade="all, delete-orphan")
    exam_questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")
    
    def __init__(self, title, description, duration_minutes):
        self.uuid = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.duration_minutes = duration_minutes
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert exam to dictionary."""
        return {
            'id': self.uuid,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'categories': [category.category for category in self.categories],
            'questions': [eq.question.uuid for eq in self.exam_questions],
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class ExamCategory(db.Model):
    """ExamCategory model for exam categories."""
    __tablename__ = 'exam_categories'
    
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50), nullable=False)
    
    # Relationships
    exam = relationship("Exam", back_populates="categories")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('exam_id', 'category', name='uq_exam_category'),
    )
    
    def __init__(self, exam_id, category):
        self.exam_id = exam_id
        self.category = category if isinstance(category, str) else category.value

class ExamQuestion(db.Model):
    """ExamQuestion model for mapping questions to exams."""
    __tablename__ = 'exam_questions'
    
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    question_order = Column(Integer, nullable=False)
    
    # Relationships
    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question", back_populates="exam_questions")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('exam_id', 'question_id', name='uq_exam_question'),
    )
    
    def __init__(self, exam_id, question_id, question_order):
        self.exam_id = exam_id
        self.question_id = question_id
        self.question_order = question_order

class ExamResult(db.Model):
    """ExamResult model for exam results."""
    __tablename__ = 'exam_results'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    completed_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="results")
    exam = relationship("Exam", back_populates="results")
    answers = relationship("ResultAnswer", back_populates="result", cascade="all, delete-orphan")
    category_scores = relationship("CategoryScore", back_populates="result", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="result", cascade="all, delete-orphan")
    
    def __init__(self, user_id, exam_id, score, max_score):
        self.uuid = str(uuid.uuid4())
        self.user_id = user_id
        self.exam_id = exam_id
        self.score = score
        self.max_score = max_score
        self.completed_at = datetime.now()
    
    def to_dict(self):
        """Convert exam result to dictionary."""
        return {
            'id': self.uuid,
            'user_id': self.user.uid,
            'exam_id': self.exam.uuid,
            'score': self.score,
            'max_score': self.max_score,
            'completed_at': self.completed_at,
            'answers': {answer.question.uuid: answer.selected_option_id for answer in self.answers},
            'category_scores': {cs.category: cs.score for cs in self.category_scores},
            'recommendations': {
                'overall': [r.recommendation_text for r in self.recommendations if r.category is None],
                'by_category': {
                    category: [r.recommendation_text for r in self.recommendations if r.category == category]
                    for category in set(r.category for r in self.recommendations if r.category is not None)
                }
            }
        }

class ResultAnswer(db.Model):
    """ResultAnswer model for answers in exam results."""
    __tablename__ = 'result_answers'
    
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('exam_results.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    selected_option_id = Column(String(50), nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    result = relationship("ExamResult", back_populates="answers")
    question = relationship("Question", back_populates="result_answers")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('result_id', 'question_id', name='uq_result_question'),
    )
    
    def __init__(self, result_id, question_id, selected_option_id, is_correct):
        self.result_id = result_id
        self.question_id = question_id
        self.selected_option_id = selected_option_id
        self.is_correct = is_correct

class CategoryScore(db.Model):
    """CategoryScore model for category-specific scores in exam results."""
    __tablename__ = 'category_scores'
    
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('exam_results.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    
    # Relationships
    result = relationship("ExamResult", back_populates="category_scores")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('result_id', 'category', name='uq_result_category'),
    )
    
    def __init__(self, result_id, category, score):
        self.result_id = result_id
        self.category = category
        self.score = score

class Recommendation(db.Model):
    """Recommendation model for AI-based recommendations in exam results."""
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('exam_results.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50), nullable=True)
    recommendation_text = Column(Text, nullable=False)
    
    # Relationships
    result = relationship("ExamResult", back_populates="recommendations")
    
    def __init__(self, result_id, recommendation_text, category=None):
        self.result_id = result_id
        self.recommendation_text = recommendation_text
        self.category = category
