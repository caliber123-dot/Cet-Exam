"""
Flask routes for authentication and user management
"""

from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
import json
import jwt
from datetime import datetime, timedelta

from services.user_service import UserService, UserRole

# Create blueprint
auth_bp = Blueprint('auth', __name__)
user_service = UserService()

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        # Verify token
        try:
            # Decode token
            secret_key = current_app.config['JWT_SECRET_KEY']
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload['sub']
            
            # Get user data
            user_data = user_service.get_user(user_id)
            if not user_data:
                raise ValueError("User not found")
                
            # Store user data in request context
            g.user = user_data
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401
    
    return decorated

# Role-based access control middleware
def role_required(role):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if g.user.get('role') != role:
                return jsonify({'message': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# Routes
@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get authentication token."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Authenticate user
    user_data = user_service.authenticate_user(data['email'], data['password'])
    if not user_data:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate JWT token
    secret_key = current_app.config['JWT_SECRET_KEY']
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    token_payload = {
        'sub': user_data['uid'],
        'exp': expiration,
        'iat': datetime.utcnow(),
        'role': user_data['role']
    }
    
    token = jwt.encode(token_payload, secret_key, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': user_data
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'displayName']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Create user
    role = data.get('role', UserRole.STUDENT)
    user_id = user_service.create_user(
        email=data['email'],
        password=data['password'],
        display_name=data['displayName'],
        role=role
    )
    
    if not user_id:
        return jsonify({'message': 'Failed to create user'}), 400
        
    return jsonify({'message': 'User created successfully', 'userId': user_id}), 201

@auth_bp.route('/users', methods=['GET'])
@role_required(UserRole.ADMIN)
def get_users():
    """Get all users (admin only)."""
    role = request.args.get('role')
    users = user_service.get_all_users(role)
    return jsonify({'users': users}), 200

@auth_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID."""
    # Check if user is requesting their own data or is an admin
    if g.user.get('uid') != user_id and g.user.get('role') != UserRole.ADMIN:
        return jsonify({'message': 'Permission denied'}), 403
        
    user_data = user_service.get_user(user_id)
    if not user_data:
        return jsonify({'message': 'User not found'}), 404
        
    return jsonify({'user': user_data}), 200

@auth_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user data."""
    # Check if user is updating their own data or is an admin
    if g.user.get('uid') != user_id and g.user.get('role') != UserRole.ADMIN:
        return jsonify({'message': 'Permission denied'}), 403
        
    data = request.get_json()
    
    # Only admins can update role
    if 'role' in data and g.user.get('role') != UserRole.ADMIN:
        return jsonify({'message': 'Permission denied to update role'}), 403
        
    success = user_service.update_user(user_id, data)
    if not success:
        return jsonify({'message': 'Failed to update user'}), 400
        
    return jsonify({'message': 'User updated successfully'}), 200

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_user(user_id):
    """Delete user (admin only)."""
    success = user_service.delete_user(user_id)
    if not success:
        return jsonify({'message': 'Failed to delete user'}), 400
        
    return jsonify({'message': 'User deleted successfully'}), 200
