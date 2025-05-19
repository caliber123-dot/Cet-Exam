"""
Flask routes for exam management
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps

from services.exam_service import ExamService
from services.grading_service import GradingService
from routes.auth_routes import token_required, role_required
from services.user_service import UserRole

# Create blueprint
exam_bp = Blueprint('exam', __name__)
exam_service = ExamService()
grading_service = GradingService()

# Routes for questions
@exam_bp.route('/questions', methods=['POST'])
@role_required(UserRole.ADMIN)
def create_question():
    """Create a new question (admin only)."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['text', 'category', 'options', 'explanation']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Create question
    question_id = exam_service.create_question(
        text=data['text'],
        category=data['category'],
        options=data['options'],
        explanation=data['explanation'],
        difficulty_level=data.get('difficulty_level', 1)
    )
    
    return jsonify({'message': 'Question created successfully', 'questionId': question_id}), 201

@exam_bp.route('/questions/<question_id>', methods=['GET'])
@token_required
def get_question(question_id):
    """Get a question by ID."""
    question = exam_service.get_question(question_id)
    if not question:
        return jsonify({'message': 'Question not found'}), 404
        
    return jsonify({'question': question.to_dict()}), 200

@exam_bp.route('/questions/<question_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_question(question_id):
    """Update a question (admin only)."""
    data = request.get_json()
    success = exam_service.update_question(question_id, data)
    if not success:
        return jsonify({'message': 'Failed to update question'}), 400
        
    return jsonify({'message': 'Question updated successfully'}), 200

@exam_bp.route('/questions/<question_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_question(question_id):
    """Delete a question (admin only)."""
    success = exam_service.delete_question(question_id)
    if not success:
        return jsonify({'message': 'Failed to delete question'}), 400
        
    return jsonify({'message': 'Question deleted successfully'}), 200

@exam_bp.route('/questions', methods=['GET'])
@token_required
def get_questions():
    """Get questions, optionally filtered by category."""
    category = request.args.get('category')
    if category:
        questions = exam_service.get_questions_by_category(category)
    else:
        # Get all questions from all categories
        categories = ['reasoning', 'english', 'computer_concepts', 'python']
        questions = []
        for cat in categories:
            questions.extend(exam_service.get_questions_by_category(cat))
            
    return jsonify({'questions': [q.to_dict() for q in questions]}), 200

# Routes for exams
@exam_bp.route('/exams', methods=['POST'])
@role_required(UserRole.ADMIN)
def create_exam():
    """Create a new exam (admin only)."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'duration_minutes', 'questions', 'categories']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Create exam
    exam_id = exam_service.create_exam(
        title=data['title'],
        description=data['description'],
        duration_minutes=data['duration_minutes'],
        question_ids=data['questions'],
        categories=data['categories']
    )
    
    return jsonify({'message': 'Exam created successfully', 'examId': exam_id}), 201

@exam_bp.route('/exams/<exam_id>', methods=['GET'])
@token_required
def get_exam(exam_id):
    """Get an exam by ID."""
    include_questions = request.args.get('include_questions', 'false').lower() == 'true'
    
    if include_questions:
        exam_data = exam_service.get_exam_with_questions(exam_id)
        if not exam_data:
            return jsonify({'message': 'Exam not found'}), 404
        return jsonify({'exam': exam_data}), 200
    else:
        exam = exam_service.get_exam(exam_id)
        if not exam:
            return jsonify({'message': 'Exam not found'}), 404
        return jsonify({'exam': exam.to_dict()}), 200

@exam_bp.route('/exams/<exam_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_exam(exam_id):
    """Update an exam (admin only)."""
    data = request.get_json()
    success = exam_service.update_exam(exam_id, data)
    if not success:
        return jsonify({'message': 'Failed to update exam'}), 400
        
    return jsonify({'message': 'Exam updated successfully'}), 200

@exam_bp.route('/exams/<exam_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_exam(exam_id):
    """Delete an exam (admin only)."""
    success = exam_service.delete_exam(exam_id)
    if not success:
        return jsonify({'message': 'Failed to delete exam'}), 400
        
    return jsonify({'message': 'Exam deleted successfully'}), 200

@exam_bp.route('/exams', methods=['GET'])
@token_required
def get_exams():
    """Get all exams."""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    exams = exam_service.get_all_exams(active_only)
    return jsonify({'exams': [e.to_dict() for e in exams]}), 200

# Routes for exam results
@exam_bp.route('/exams/<exam_id>/submit', methods=['POST'])
@token_required
def submit_exam(exam_id):
    """Submit an exam for grading."""
    data = request.get_json()
    
    # Validate required fields
    if 'answers' not in data:
        return jsonify({'message': 'Missing required field: answers'}), 400
    
    # Grade exam
    try:
        user_id = g.user.get('uid')
        result_id = grading_service.grade_exam(
            user_id=user_id,
            exam_id=exam_id,
            answers=data['answers']
        )
        
        return jsonify({
            'message': 'Exam graded successfully', 
            'resultId': result_id
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'Error grading exam: {str(e)}'}), 500

@exam_bp.route('/results/<result_id>', methods=['GET'])
@token_required
def get_result(result_id):
    """Get an exam result by ID."""
    result = grading_service.get_exam_result(result_id)
    if not result:
        return jsonify({'message': 'Result not found'}), 404
        
    # Check if user is requesting their own result or is an admin
    if g.user.get('uid') != result.get('user_id') and g.user.get('role') != UserRole.ADMIN:
        return jsonify({'message': 'Permission denied'}), 403
        
    return jsonify({'result': result}), 200

@exam_bp.route('/users/<user_id>/results', methods=['GET'])
@token_required
def get_user_results(user_id):
    """Get all exam results for a user."""
    # Check if user is requesting their own results or is an admin
    if g.user.get('uid') != user_id and g.user.get('role') != UserRole.ADMIN:
        return jsonify({'message': 'Permission denied'}), 403
        
    results = grading_service.get_user_results(user_id)
    return jsonify({'results': results}), 200
