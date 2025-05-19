"""
Grading service for the CET Exam App with PostgreSQL
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from database import db
from models.sql_models import (
    Question, Option, Exam, ExamResult, ResultAnswer, 
    CategoryScore, Recommendation, User, SubjectCategory, ExamQuestion
)

class GradingService:
    """Service for grading exams and providing recommendations."""
    
    def grade_exam(self, user_id: str, exam_id: str, answers: Dict[str, str]) -> str:
        """
        Grade an exam based on user answers.
        
        Args:
            user_id: ID of the user taking the exam
            exam_id: ID of the exam being taken
            answers: Dictionary mapping question IDs to selected option IDs
            
        Returns:
            str: ID of the created exam result
        """
        try:
            # Get user and exam
            user = User.query.filter_by(uid=user_id).first()
            if not user:
                raise ValueError("User not found")
                
            exam = Exam.query.filter_by(uuid=exam_id).first()
            if not exam:
                raise ValueError("Exam not found")
                
            # Get all questions for this exam
            exam_questions = ExamQuestion.query.filter_by(exam_id=exam.id).all()
            if not exam_questions:
                raise ValueError("Exam has no questions")
                
            # Calculate score and prepare explanations
            total_questions = len(exam_questions)
            correct_count = 0
            category_scores = {}
            question_results = {}
            
            for eq in exam_questions:
                question = eq.question
                q_id = question.uuid
                
                # Get correct option
                correct_option = None
                for option in question.options:
                    if option.is_correct:
                        correct_option = option.option_id
                        break
                
                if q_id not in answers:
                    # Question not answered
                    question_results[q_id] = {
                        'correct': False,
                        'selected_option': None,
                        'correct_option': correct_option,
                        'explanation': question.explanation
                    }
                    continue
                    
                selected_option = answers[q_id]
                is_correct = selected_option == correct_option
                
                # Update question result
                question_results[q_id] = {
                    'correct': is_correct,
                    'selected_option': selected_option,
                    'correct_option': correct_option,
                    'explanation': question.explanation
                }
                
                # Update scores
                if is_correct:
                    correct_count += 1
                    
                # Update category scores
                category = question.category
                if category not in category_scores:
                    category_scores[category] = {
                        'total': 0,
                        'correct': 0
                    }
                category_scores[category]['total'] += 1
                if is_correct:
                    category_scores[category]['correct'] += 1
            
            # Calculate final scores
            score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
            # Calculate category percentages
            category_percentages = {}
            for category, counts in category_scores.items():
                if counts['total'] > 0:
                    category_percentages[category] = (counts['correct'] / counts['total']) * 100
                else:
                    category_percentages[category] = 0
            
            # Generate recommendations
            recommendations = self._generate_recommendations(category_percentages, question_results)
            
            # Create result object
            result = ExamResult(
                user_id=user.id,
                exam_id=exam.id,
                score=score,
                max_score=100.0
            )
            
            db.session.add(result)
            db.session.flush()  # Flush to get the result ID
            
            # Save answers
            for q_id, result_data in question_results.items():
                question = Question.query.filter_by(uuid=q_id).first()
                if question:
                    answer = ResultAnswer(
                        result_id=result.id,
                        question_id=question.id,
                        selected_option_id=result_data['selected_option'],
                        is_correct=result_data['correct']
                    )
                    db.session.add(answer)
            
            # Save category scores
            for category, score_value in category_percentages.items():
                category_score = CategoryScore(
                    result_id=result.id,
                    category=category,
                    score=score_value
                )
                db.session.add(category_score)
            
            # Save recommendations
            # Overall recommendations
            for rec_text in recommendations['overall']:
                recommendation = Recommendation(
                    result_id=result.id,
                    recommendation_text=rec_text
                )
                db.session.add(recommendation)
            
            # Category-specific recommendations
            for category, rec_list in recommendations['by_category'].items():
                for rec_text in rec_list:
                    recommendation = Recommendation(
                        result_id=result.id,
                        category=category,
                        recommendation_text=rec_text
                    )
                    db.session.add(recommendation)
            
            db.session.commit()
            return result.uuid
        except Exception as e:
            db.session.rollback()
            print(f"Error grading exam: {e}")
            raise
    
    def get_exam_result(self, result_id: str) -> Optional[Dict]:
        """Get an exam result by ID with detailed information."""
        try:
            result = ExamResult.query.filter_by(uuid=result_id).first()
            if not result:
                return None
                
            return result.to_dict()
        except Exception as e:
            print(f"Error getting exam result: {e}")
            return None
    
    def get_user_results(self, user_id: str) -> List[Dict]:
        """Get all exam results for a specific user."""
        try:
            user = User.query.filter_by(uid=user_id).first()
            if not user:
                return []
                
            results = ExamResult.query.filter_by(user_id=user.id).all()
            return [result.to_dict() for result in results]
        except Exception as e:
            print(f"Error getting user results: {e}")
            return []
    
    def _generate_recommendations(self, category_scores: Dict[str, float], 
                                 question_results: Dict[str, Dict]) -> Dict[str, List[str]]:
        """
        Generate AI-based recommendations based on exam performance.
        
        Args:
            category_scores: Dictionary mapping categories to percentage scores
            question_results: Dictionary mapping question IDs to result data
            
        Returns:
            Dictionary with recommendations by category and overall
        """
        recommendations = {
            'overall': [],
            'by_category': {}
        }
        
        # Overall performance assessment
        avg_score = sum(category_scores.values()) / len(category_scores) if category_scores else 0
        
        if avg_score >= 90:
            recommendations['overall'].append("Excellent performance! Consider exploring advanced topics.")
        elif avg_score >= 70:
            recommendations['overall'].append("Good performance. Focus on the categories where you scored lower.")
        elif avg_score >= 50:
            recommendations['overall'].append("Average performance. Review the explanations for questions you got wrong.")
        else:
            recommendations['overall'].append("You need more practice. Focus on understanding the basic concepts first.")
        
        # Category-specific recommendations
        for category, score in category_scores.items():
            cat_recommendations = []
            
            # Convert category string to readable format
            readable_category = category.replace('_', ' ').title()
            
            if score < 50:
                cat_recommendations.append(f"Review the fundamentals of {readable_category}.")
                
                # Add specific recommendations based on category
                if category == SubjectCategory.REASONING.value:
                    cat_recommendations.append("Practice logical reasoning puzzles and pattern recognition exercises.")
                elif category == SubjectCategory.ENGLISH.value:
                    cat_recommendations.append("Focus on grammar rules and vocabulary building.")
                elif category == SubjectCategory.COMPUTER_CONCEPTS.value:
                    cat_recommendations.append("Study basic computer architecture and operating system concepts.")
                elif category == SubjectCategory.PYTHON.value:
                    cat_recommendations.append("Practice basic Python syntax and simple programming exercises.")
            
            elif score < 70:
                cat_recommendations.append(f"You have a basic understanding of {readable_category}. Practice more complex problems.")
                
                # Add specific recommendations based on category
                if category == SubjectCategory.REASONING.value:
                    cat_recommendations.append("Work on analytical reasoning and critical thinking problems.")
                elif category == SubjectCategory.ENGLISH.value:
                    cat_recommendations.append("Practice reading comprehension and sentence correction exercises.")
                elif category == SubjectCategory.COMPUTER_CONCEPTS.value:
                    cat_recommendations.append("Learn about networking concepts and database fundamentals.")
                elif category == SubjectCategory.PYTHON.value:
                    cat_recommendations.append("Study data structures and algorithms in Python.")
            
            else:
                cat_recommendations.append(f"You have a good grasp of {readable_category}. Focus on advanced topics.")
                
                # Add specific recommendations based on category
                if category == SubjectCategory.REASONING.value:
                    cat_recommendations.append("Challenge yourself with complex logical puzzles and advanced reasoning problems.")
                elif category == SubjectCategory.ENGLISH.value:
                    cat_recommendations.append("Work on advanced writing skills and complex comprehension passages.")
                elif category == SubjectCategory.COMPUTER_CONCEPTS.value:
                    cat_recommendations.append("Explore cloud computing, cybersecurity, and emerging technologies.")
                elif category == SubjectCategory.PYTHON.value:
                    cat_recommendations.append("Learn advanced Python concepts like decorators, generators, and concurrent programming.")
            
            recommendations['by_category'][category] = cat_recommendations
        
        # Add recommendation for frequently missed concepts
        missed_concepts = self._identify_missed_concepts(question_results)
        if missed_concepts:
            recommendations['overall'].append(f"Focus on these frequently missed concepts: {', '.join(missed_concepts)}.")
        
        return recommendations
    
    def _identify_missed_concepts(self, question_results: Dict[str, Dict]) -> List[str]:
        """Identify concepts that were frequently missed in the exam."""
        # This is a simplified implementation
        # In a real system, this would analyze question content and patterns
        missed_concepts = []
        
        # Count incorrect questions by looking for patterns in explanations
        explanation_keywords = {}
        
        for q_id, result in question_results.items():
            if not result['correct']:
                # Extract keywords from explanation (simplified)
                explanation = result['explanation'].lower()
                words = explanation.split()
                
                # Count significant words (longer than 4 characters)
                for word in words:
                    if len(word) > 4 and word.isalpha():
                        explanation_keywords[word] = explanation_keywords.get(word, 0) + 1
        
        # Find the most common keywords (concepts)
        if explanation_keywords:
            sorted_keywords = sorted(explanation_keywords.items(), key=lambda x: x[1], reverse=True)
            missed_concepts = [keyword.title() for keyword, count in sorted_keywords[:3] if count > 1]
        
        return missed_concepts
