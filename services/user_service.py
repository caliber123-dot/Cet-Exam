"""
User service for the CET Exam App with PostgreSQL
"""

from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Union

from database import db
from models.sql_models import User

class UserRole:
    """User role constants."""
    ADMIN = "admin"
    STUDENT = "student"

class UserService:
    """Service for managing users and authentication."""
    
    def create_user(self, email: str, password: str, display_name: str, role: str = UserRole.STUDENT) -> Optional[str]:
        """
        Create a new user.
        
        Args:
            email: User email address
            password: User password
            display_name: User display name
            role: User role (admin or student)
            
        Returns:
            str: User ID if successful, None otherwise
        """
        try:
            # Validate role
            if role not in [UserRole.ADMIN, UserRole.STUDENT]:
                raise ValueError(f"Invalid role: {role}")
                
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                raise ValueError(f"User with email {email} already exists")
                
            # Hash password
            password_hash = generate_password_hash(password)
            
            # Create user
            user = User(
                email=email,
                display_name=display_name,
                password_hash=password_hash,
                role=role
            )
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            return str(user.uid)
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data by ID."""
        try:
            user = User.query.filter_by(uid=user_id).first()
            if user:
                return user.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user data by email."""
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                return user.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user data."""
        try:
            user = User.query.filter_by(uid=user_id).first()
            if not user:
                return False
                
            # Update fields
            if 'email' in updates:
                user.email = updates['email']
            if 'displayName' in updates:
                user.display_name = updates['displayName']
            if 'role' in updates:
                user.role = updates['role']
            if 'password' in updates:
                user.password_hash = generate_password_hash(updates['password'])
                
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            user = User.query.filter_by(uid=user_id).first()
            if not user:
                return False
                
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user: {e}")
            return False
    
    def get_all_users(self, role: Optional[str] = None) -> List[Dict]:
        """
        Get all users, optionally filtering by role.
        
        Args:
            role: Optional role filter (admin or student)
            
        Returns:
            List of user data dictionaries
        """
        try:
            if role:
                # Validate role
                if role not in [UserRole.ADMIN, UserRole.STUDENT]:
                    raise ValueError(f"Invalid role: {role}")
                    
                users = User.query.filter_by(role=role).all()
            else:
                users = User.query.all()
                
            return [user.to_dict() for user in users]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            user = User.query.filter_by(uid=user_id).first()
            if not user:
                return False
                
            user.last_login = datetime.now()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating last login: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with user data if authentication successful, None otherwise
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return None
                
            # Check password
            if not check_password_hash(user.password_hash, password):
                return None
                
            # Update last login
            user.last_login = datetime.now()
            db.session.commit()
            
            return user.to_dict()
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def has_role(self, user_id: str, required_role: str) -> bool:
        """
        Check if user has the required role.
        
        Args:
            user_id: User ID to check
            required_role: Role to check for
            
        Returns:
            True if user has the required role, False otherwise
        """
        try:
            user = User.query.filter_by(uid=user_id).first()
            if not user:
                return False
                
            return user.role == required_role
        except Exception as e:
            print(f"Error checking role: {e}")
            return False
