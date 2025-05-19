"""
Exam service for the CET Exam App with PostgreSQL
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional, Union

from database import db
from models.sql_models import (
    Question, Option, Exam, ExamCategory, ExamQuestion, 
    User, SubjectCategory
)

class ExamService:
    """Service for managing exams and questions."""
    
    def create_question(self, 
                       text: str, 
                       category: Union[str, SubjectCategory], 
                       options: List[Dict], 
                       explanation: str,
                       difficulty_level: int = 1) -> str:
        """
        Create a new question in the database.
        
        Args:
            text: The question text
            category: Subject category (reasoning, english, computer_concepts, python)
            options: List of option dictionaries with text and is_correct flag
            explanation: Explanation for the correct answer
            difficulty_level: Difficulty level (1-Easy, 2-Medium, 3-Hard)
            
        Returns:
            str: ID of the created question
        """
        try:
            # Convert string category to enum if needed
            if isinstance(category, str):
                category = category
            elif isinstance(category, SubjectCategory):
                category = category.value
                
            # Create question
            question = Question(
                text=text,
                category=category,
                explanation=explanation,
                difficulty_level=difficulty_level
            )
            
            db.session.add(question)
            db.session.flush()  # Flush to get the question ID
            
            # Create options
            for i, opt in enumerate(options):
                option = Option(
                    question_id=question.id,
                    option_id=str(i+1),
                    text=opt.get('text', ''),
                    is_correct=opt.get('is_correct', False)
                )
                db.session.add(option)
            
            db.session.commit()
            return question.uuid
        except Exception as e:
            db.session.rollback()
            print(f"Error creating question: {e}")
            raise
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """Get a question by ID."""
        try:
            return Question.query.filter_by(uuid=question_id).first()
        except Exception as e:
            print(f"Error getting question: {e}")
            return None
    
    def update_question(self, question_id: str, updates: Dict) -> bool:
        """Update a question with the provided fields."""
        try:
            question = Question.query.filter_by(uuid=question_id).first()
            if not question:
                return False
                
            # Update question fields
            if 'text' in updates:
                question.text = updates['text']
            if 'category' in updates:
                category = updates['category']
                if isinstance(category, SubjectCategory):
                    category = category.value
                question.category = category
            if 'explanation' in updates:
                question.explanation = updates['explanation']
            if 'difficulty_level' in updates:
                question.difficulty_level = updates['difficulty_level']
                
            # Update options if provided
            if 'options' in updates:
                # Delete existing options
                Option.query.filter_by(question_id=question.id).delete()
                
                # Create new options
                for i, opt in enumerate(updates['options']):
                    option = Option(
                        question_id=question.id,
                        option_id=str(i+1),
                        text=opt.get('text', ''),
                        is_correct=opt.get('is_correct', False)
                    )
                    db.session.add(option)
            
            question.updated_at = datetime.now()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating question: {e}")
            return False
    
    def delete_question(self, question_id: str) -> bool:
        """Delete a question by ID."""
        try:
            question = Question.query.filter_by(uuid=question_id).first()
            if not question:
                return False
                
            db.session.delete(question)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting question: {e}")
            return False
    
    def get_questions_by_category(self, category: Union[str, SubjectCategory]) -> List[Question]:
        """Get all questions for a specific category."""
        try:
            if isinstance(category, SubjectCategory):
                category = category.value
                
            return Question.query.filter_by(category=category).all()
        except Exception as e:
            print(f"Error getting questions by category: {e}")
            return []
    
    def create_exam(self, 
                   title: str, 
                   description: str, 
                   duration_minutes: int,
                   question_ids: List[str],
                   categories: List[Union[str, SubjectCategory]]) -> str:
        """
        Create a new exam in the database.
        
        Args:
            title: Exam title
            description: Exam description
            duration_minutes: Duration in minutes
            question_ids: List of question IDs to include
            categories: List of subject categories covered
            
        Returns:
            str: ID of the created exam
        """
        try:
            # Create exam
            exam = Exam(
                title=title,
                description=description,
                duration_minutes=duration_minutes
            )
            
            db.session.add(exam)
            db.session.flush()  # Flush to get the exam ID
            
            # Add categories
            for cat in categories:
                if isinstance(cat, SubjectCategory):
                    cat = cat.value
                    
                exam_category = ExamCategory(
                    exam_id=exam.id,
                    category=cat
                )
                db.session.add(exam_category)
            
            # Add questions
            for i, q_id in enumerate(question_ids):
                question = Question.query.filter_by(uuid=q_id).first()
                if question:
                    exam_question = ExamQuestion(
                        exam_id=exam.id,
                        question_id=question.id,
                        question_order=i
                    )
                    db.session.add(exam_question)
            
            db.session.commit()
            return exam.uuid
        except Exception as e:
            db.session.rollback()
            print(f"Error creating exam: {e}")
            raise
    
    def get_exam(self, exam_id: str) -> Optional[Exam]:
        """Get an exam by ID."""
        try:
            return Exam.query.filter_by(uuid=exam_id).first()
        except Exception as e:
            print(f"Error getting exam: {e}")
            return None
    
    def update_exam(self, exam_id: str, updates: Dict) -> bool:
        """Update an exam with the provided fields."""
        try:
            exam = Exam.query.filter_by(uuid=exam_id).first()
            if not exam:
                return False
                
            # Update exam fields
            if 'title' in updates:
                exam.title = updates['title']
            if 'description' in updates:
                exam.description = updates['description']
            if 'duration_minutes' in updates:
                exam.duration_minutes = updates['duration_minutes']
            if 'is_active' in updates:
                exam.is_active = updates['is_active']
                
            # Update categories if provided
            if 'categories' in updates:
                # Delete existing categories
                ExamCategory.query.filter_by(exam_id=exam.id).delete()
                
                # Add new categories
                for cat in updates['categories']:
                    if isinstance(cat, SubjectCategory):
                        cat = cat.value
                        
                    exam_category = ExamCategory(
                        exam_id=exam.id,
                        category=cat
                    )
                    db.session.add(exam_category)
            
            # Update questions if provided
            if 'questions' in updates:
                # Delete existing questions
                ExamQuestion.query.filter_by(exam_id=exam.id).delete()
                
                # Add new questions
                for i, q_id in enumerate(updates['questions']):
                    question = Question.query.filter_by(uuid=q_id).first()
                    if question:
                        exam_question = ExamQuestion(
                            exam_id=exam.id,
                            question_id=question.id,
                            question_order=i
                        )
                        db.session.add(exam_question)
            
            exam.updated_at = datetime.now()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating exam: {e}")
            return False
    
    def delete_exam(self, exam_id: str) -> bool:
        """Delete an exam by ID."""
        try:
            exam = Exam.query.filter_by(uuid=exam_id).first()
            if not exam:
                return False
                
            db.session.delete(exam)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting exam: {e}")
            return False
    
    def get_all_exams(self, active_only: bool = True) -> List[Exam]:
        """Get all exams, optionally filtering for active only."""
        try:
            if active_only:
                return Exam.query.filter_by(is_active=True).all()
            else:
                return Exam.query.all()
        except Exception as e:
            print(f"Error getting exams: {e}")
            return []
    
    def get_exam_with_questions(self, exam_id: str) -> Optional[Dict]:
        """
        Get an exam with all its questions fully populated.
        
        Returns a dictionary with exam data and a list of question objects.
        """
        try:
            exam = Exam.query.filter_by(uuid=exam_id).first()
            if not exam:
                return None
                
            # Get all questions for this exam
            questions = []
            for eq in exam.exam_questions:
                question = eq.question
                if question:
                    questions.append(question.to_dict())
                    
            # Return combined data
            result = exam.to_dict()
            result['question_data'] = questions
            return result
        except Exception as e:
            print(f"Error getting exam with questions: {e}")
            return None
